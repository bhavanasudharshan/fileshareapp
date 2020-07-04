import requests
import boto3
from requests_aws4auth import AWS4Auth
# b'<?xml version="1.0" encoding="UTF-8"?>\n<InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Bucket>file-share-test</Bucket><Key>example-object</Key><UploadId>PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql</UploadId></InitiateMultipartUploadResult>'

# {'x-amz-id-2': '8l3FcsjbxQDWfaxmTirYKugBGxdzS9AOBzMRkrmvL+50TFlYv1eK5WwSdDq7Y0guoeMbezsmJY0=', 'x-amz-request-id': 'AFAD35FBDFBFE442', 'Date': 'Fri, 03 Jul 2020 22:06:40 GMT', 'Transfer-Encoding': 'chunked', 'Server': 'AmazonS3'}
    # host = 'file-share-test.s3-us-west-2.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

region = 'us-west-2'  # e.g. us-west-1
service = 's3'
credentials = boto3.Session().get_credentials()
auth=AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# response = requests.post("https://file-share-test.s3-us-west-2.amazonaws.com/example-object?uploads", auth=auth)


# response=requests.put("http://file-share-test.s3-us-west-2.amazonaws.com/example-object?partNumber=1&uploadId=PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql",auth=auth,data={"hi":"bye"})
# print(response.status_code)
#
# response=requests.put("http://file-share-test.s3-us-west-2.amazonaws.com/example-object?partNumber=2&uploadId=PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql",auth=auth,data={"d":"end"})
# print(response.status_code)
# response=requests.get("http://file-share-test.s3-us-west-2.amazonaws.com/example-object?MaxParts=3&PartNumberMarker=1&uploadId=PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql",auth=auth)
# print(response.content)

x='<?xml version="1.0" encoding="UTF-8"?><CompleteMultipartUpload xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Part><ETag>"cbf77c9ded075b0afff9ff00a6bae14e"</ETag><PartNumber>1</PartNumber></Part><Part><ETag>"094b1c8d3d5cdbeb393dd2027e714f1a"</ETag><PartNumber>2</PartNumber></Part></CompleteMultipartUpload>'

headers={'Content-Type':"application/xml"}
# response=requests.post("http://file-share-test.s3-us-west-2.amazonaws.com/example-object?uploadId=PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql",data=dict(CompleteMultipartUpload='<?xml version="1.0" encoding="UTF-8"?><CompleteMultipartUpload xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Part><PartNumber>1</PartNumber><Etag>"cbf77c9ded075b0afff9ff00a6bae14e"</Etag></Part><Part><PartNumber>2</PartNumber><Etag>"094b1c8d3d5cdbeb393dd2027e714f1a"</Etag></Part></CompleteMultipartUpload>'),headers=headers)
# print(response.status_code)


response=requests.post("http://file-share-test.s3-us-west-2.amazonaws.com/example-object?uploadId=PbcBo5wRAWaP9fWKIS3aOfYpds1Ezk6dkhBc5D5zmrCnq0jJrdBqPIr_LaorvWP.pX361YEgHvRwB5kAhfRN0tmbFsKhHXtc4fKPQ9XwIZ8sBiPpt9x_dyXigU4bMEql",data=dict(CompleteMultipartUpload=x),headers=headers,auth=auth)
print(response.status_code)