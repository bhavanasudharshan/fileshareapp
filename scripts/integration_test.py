import base64
import os
import random
import string

import requests
from flask import json

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str


username = get_random_string(8)
password = '123456'
#
response = requests.post("http://localhost:8081/register", verify=False, auth=(username, password),
                         headers={'Content-Type': 'application/json'})
assert response.status_code == 201
#
response = requests.post("http://localhost:8081/login", verify=False, auth=(username, password),
                         headers={'Content-Type': 'application/json'})
assert response.status_code == 200

access_token = json.loads(response.text)['access_token']
access_token_auth = "access_token {0}".format(access_token)
#
filepath="christfriends.png"
file_size = os.stat(filepath).st_size
print(file_size)

resp = requests.post("http://0.0.0.0:8080/upload", data=dict(upload_phase='start', size=file_size),
                     headers=dict(
                         Authorization=access_token_auth))

decoded_resp = resp.content.decode('utf-8')
response_json = json.loads(decoded_resp)

start_offset = (response_json['start_offset'])
end_offset = (response_json['end_offset'])
upload_session_id = (response_json['upload_session_id'])
upload_id=(response_json['upload_id'])

f = open(filepath, "rb")

encoded_test=[]

while start_offset != end_offset:
    s = start_offset
    f.seek(s)
    read_size=end_offset-start_offset
    b = f.read(read_size)


    base64_bytes = base64.b64encode(b)
    video_chunk = base64_bytes.decode('utf-8')
    encoded_test.append(video_chunk)


    print(video_chunk)
    print("\n")

    resp = requests.post("http://0.0.0.0:8080/upload",
                         data=dict(upload_phase='transfer', upload_session_id=upload_session_id,
                                   video_file_chunk=video_chunk),
                         headers=dict(
                             Authorization=access_token_auth))

    decoded_resp = resp.content.decode('utf-8')
    response_json = json.loads(decoded_resp)

    start_offset = (response_json['start_offset'])
    end_offset = (response_json['end_offset'])


byte_test=bytearray()

resp = requests.get("http://0.0.0.0:8082/download/"+upload_id,
                     headers=dict(
                         Authorization=access_token_auth))

decoded_resp = resp.content.decode('utf-8')
response_json = json.loads(decoded_resp)

print(response_json['chunk'])
print("\n")

chunk_size=int(response_json['total_chunks']) #16
chunk_number=1

chunk = response_json['chunk']

c = chunk.encode('utf-8')
bc = base64.b64decode(c)
byte_test.extend(bc)

chunk_size=chunk_size-1

while chunk_size>=1:
    print(chunk_size)
    resp = requests.get("http://0.0.0.0:8082/download/" + upload_id,
                        headers=dict(
                            Authorization=access_token_auth),data=dict(chunk_number=str(chunk_number)))
                            # Authorization=access_token_auth),data=dict(chunk_number=str(15)))

    decoded_resp = resp.content.decode('utf-8')
    response_json = json.loads(decoded_resp)
    print(response_json['chunk'])
    print("\n")

    chunk=response_json['chunk']
    c = chunk.encode('utf-8')
    bc=base64.b64decode(c)

    byte_test.extend(bc)

    chunk_number= chunk_number + 1
    chunk_size=chunk_size-1
    print(chunk_number)

print(byte_test)
f = open("demofile2.png", "wb")
f.write(byte_test)
f.close()