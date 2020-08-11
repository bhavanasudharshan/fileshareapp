from functools import wraps
from http import HTTPStatus
import jwt
from bson.objectid import ObjectId
from flask import Flask, Response, json
from flask import request, jsonify

from mongodb_client import get_db
from redis_client import get_cache

global UPLOAD_MAX_SIZE
UPLOAD_MAX_SIZE = 2500635
CHUNK_SIZE = 100000
# 416407

app = Flask(__name__)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token.encode('UTF-8'), 'SECRET', algorithm='HS256')
            print("logged in user is ")
            print(data)
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})
        return f(*args, **kwargs)

    return decorator


@app.route('/')
def index():
    resp = Response()
    resp.set_data('Welcome to CRM! Please Login')
    return resp


@app.route('/uploadshare/<uploadId>/<shareUserId>', methods=["POST"])
@token_required
def uploadshare(uploadId, shareUserId):
    r = Response(mimetype="application/json")
    r.headers["Content-Type"] = "text/json; charset=utf-8"

    token = request.headers['Authorization'].split(' ')[1]
    data = jwt.decode(token.encode('UTF-8'), 'SECRET', algorithm='HS256')

    upload = get_db().uploads.find_one({'_id': ObjectId(uploadId), 'status': 'done', 'ownerid': data['sub']})

    if upload is None:
        r.response = json.dumps({'error': 'upload id not found'})
        r.status_code = HTTPStatus.NOT_FOUND
        return r

    u = get_db().users.find_one({"name": shareUserId})
    if u is None:
        r.response = json.dumps({'error': 'user not found'})
        r.status_code = HTTPStatus.NOT_FOUND
        return r

    if shareUserId in upload['users']:
        r.response = json.dumps({'status': 'already shared'})
        r.status_code = HTTPStatus.OK
        return r

    get_db().uploads.update_one({'_id': ObjectId(uploadId)}, {'$push': {'users': shareUserId}})
    r.response = json.dumps({'status': 'share success'})
    r.status_code = HTTPStatus.OK
    return r


@app.route('/upload', methods=["POST"])
@token_required
def upload():
    r = Response(mimetype="application/json")
    r.headers["Content-Type"] = "text/json; charset=utf-8"

    if 'upload_phase' in request.values and request.values['upload_phase'] == 'start':
        if 'size' not in request.values:
            r.response = json.dumps({'error': 'provide file size'})
            r.status_code = HTTPStatus.BAD_REQUEST
            return r
        else:

            if UPLOAD_MAX_SIZE < int(request.values['size']):
                r.response = json.dumps({'error': 'file too large'})
                r.status_code = HTTPStatus.BAD_REQUEST
                return r

            else:
                # create a session
                size = int(request.values['size'])
                new_session_id = get_cache().incr("upload:session:id", 1)
                token = request.headers['Authorization'].split(' ')[1]
                data = jwt.decode(token.encode('UTF-8'), 'SECRET', algorithm='HS256')

                table = get_db()['uploads']
                mydict = {'status': 'start','users':[data['sub']]}

                x = table.insert_one(mydict)
                upload_id = x.inserted_id

                upload_redis_key = "{0}:{1}".format("upload:session", new_session_id)

                get_cache().hset(upload_redis_key, "state", "start")
                get_cache().hset(upload_redis_key, "size", size)
                get_cache().hset(upload_redis_key, "start_offset", 0)
                get_cache().hset(upload_redis_key, "upload_id", str(upload_id))

                start_offset = 0
                end_offset = CHUNK_SIZE

                if size <= CHUNK_SIZE:
                    end_offset = size

                get_cache().hset(upload_redis_key, "end_offset", end_offset)

                response_body = {
                    'upload_session_id': new_session_id,
                    'upload_id': str(upload_id),
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                }
                r.response = json.dumps(response_body)
                r.status_code = HTTPStatus.OK

    else:
        if 'upload_session_id' not in request.values or 'video_file_chunk' not in request.values:
            r.response = json.dumps({'error': 'provide upload session id and video file chunk'})
            r.status_code = HTTPStatus.BAD_REQUEST
            return r

        upload_session_id = request.values['upload_session_id']
        upload_redis_key = "{0}:{1}".format("upload:session", upload_session_id)
        uploadid = get_cache().hget(upload_redis_key, 'upload_id')

        start_offset = int(get_cache().hget(upload_redis_key, 'end_offset'))
        end_offset = int(get_cache().hget(upload_redis_key, 'end_offset'))
        size = int(get_cache().hget(upload_redis_key, 'size'))
        print(end_offset)

        if end_offset == size:
            response_body = {
                'upload_session_id': upload_session_id,
                'uploadid': uploadid,
                'start_offset': end_offset,
                'end_offset': end_offset,
                'status': 'done'
            }
            # complete it
            r.response = json.dumps(response_body)
            token = request.headers['Authorization'].split(' ')[1]
            data = jwt.decode(token.encode('UTF-8'), 'SECRET', algorithm='HS256')
            get_db()['uploads'].update_one({'_id': ObjectId(uploadid)},
                                           {'$set': {'ownerid': data['sub'], 'status': 'done'}})

            # get_db()['users'].update({'name': data['sub']}, {'$push': {'uploads': uploadid}})

        elif (start_offset + CHUNK_SIZE) >= size:
            end_offset = size
            response_body = {
                'upload_session_id': upload_session_id,
                'uploadid': uploadid,
                'start_offset': start_offset,
                'end_offset': end_offset,
            }
            r.response = json.dumps(response_body)

        else:
            end_offset = start_offset + CHUNK_SIZE
            # start_offset = start_offset
            response_body = {
                'upload_session_id': upload_session_id,
                'uploadid':uploadid,
                'start_offset': start_offset,
                'end_offset': end_offset,
            }
            r.response = json.dumps(response_body)
        get_cache().hset(upload_redis_key, "start_offset", start_offset)
        get_cache().hset(upload_redis_key, "end_offset", end_offset)

        video_file_chunk = request.values['video_file_chunk']
        uploadid = get_cache().hget(upload_redis_key, 'upload_id')
        print(video_file_chunk)

        get_db()['uploads'].update_one({'_id': ObjectId(uploadid)}, {'$push': {'chunks': video_file_chunk}})
    return r


if __name__ == "__main__":
    # app.run(port=8081)
    app.run(host="0.0.0.0")
    # ,ssl_context=("/etc/ssl/certs/pythonusersapi/cert.pem","/etc/ssl/certs/pythonusersapi/key.pem"),port=8081)
