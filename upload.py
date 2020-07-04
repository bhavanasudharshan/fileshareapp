from functools import wraps
from http import HTTPStatus

import jwt
from flask import Flask, Response
from flask import request, jsonify
from rest_framework.utils import json

from redis_client import get_cache

global UPLOAD_MAX_SIZE
UPLOAD_MAX_SIZE = 50000
CHUNK_SIZE = 100000
app = Flask(__name__)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'access-token' in request.cookies:
            token = request.cookies['access-token']

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


@app.route('/upload', methods=["POST"])
# @token_required
def upload():
    r = Response(mimetype="application/json")
    r.headers["Content-Type"] = "text/json; charset=utf-8"

    if 'upload_phase' in request.values and request.values['upload_phase'] == 'start':
        if 'size' not in request.values:
            r.response = json.dumps({'error': 'provide file size'})
            r.status_code = HTTPStatus.BAD_REQUEST
            return r
        else:

            if UPLOAD_MAX_SIZE > int(request.values['size']):
                r.response = json.dumps({'error': 'file too large'})
                r.status_code = HTTPStatus.BAD_REQUEST
                return r

            else:

                # create a session
                size = int(request.values['size'])
                new_session_id = get_cache().incr("upload:session:id", 1)
                new_video_id = get_cache().incr("upload:video:id", 1)
                upload_redis_key = "{0}:{1}".format("upload:session", new_session_id)

                get_cache().hset(upload_redis_key, "state", "start")
                get_cache().hset(upload_redis_key, "size", size)
                get_cache().hset(upload_redis_key, "start_offset", 1)
                get_cache().hset(upload_redis_key,"video_id",new_video_id)

                start_offset = 0
                end_offset = CHUNK_SIZE

                if size <= CHUNK_SIZE:
                    end_offset = size

                get_cache().hset(upload_redis_key, "end_offset", end_offset)

                response_body = {
                    'upload_session_id': new_session_id,
                    'new_video_id':new_video_id,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                }
                r.response = json.dumps(response_body)
                print(r.response)
                r.status_code = HTTPStatus.OK

    else:
        if 'upload_session_id' not in request.values or 'video_file_chunk' not in request.values:
            r.response = json.dumps({'error': 'provide upload session id and video file chunk'})
            r.status_code = HTTPStatus.BAD_REQUEST
            return r

        upload_session_id = request.values['upload_session_id']
        upload_redis_key = "{0}:{1}".format("upload:session", upload_session_id)
        start_offset = int(get_cache().hget(upload_redis_key, 'end_offset'))
        end_offset = int(get_cache().hget(upload_redis_key, 'end_offset'))
        size = int(get_cache().hget(upload_redis_key, 'size'))

        if end_offset == size:
            response_body = {
                'upload_session_id': upload_session_id,
                'start_offset': end_offset,
                'end_offset': end_offset,
            }
            r.response = json.dumps(response_body)

        elif (start_offset + CHUNK_SIZE + 1) > size:
            end_offset = size
            response_body = {
                'upload_session_id': upload_session_id,
                'start_offset': start_offset,
                'end_offset': end_offset,
            }
            r.response = json.dumps(response_body)

        else:
            end_offset = start_offset + CHUNK_SIZE
            start_offset = start_offset + 1
            response_body = {
                'upload_session_id': upload_session_id,
                'start_offset': start_offset,
                'end_offset': end_offset,
                'status': 'stop'
            }
            r.response = json.dumps(response_body)
        get_cache().hset(upload_redis_key, "start_offset", start_offset)
        get_cache().hset(upload_redis_key, "end_offset", end_offset)
    return r

if __name__ == "__main__":
        # app.run(port=8081)
    app.run(host="0.0.0.0", port=8081)
        # ,ssl_context=("/etc/ssl/certs/pythonusersapi/cert.pem","/etc/ssl/certs/pythonusersapi/key.pem"),port=8081)
