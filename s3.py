# from aws_requests_auth.aws_auth import AWSRequestsAuth
import boto3

# reuse the http connection , have a pool of connections.
# measure the network bandwidth taken by each upload and then decide on the parallel requests.
# check DNS and make sure s3 check requests are spread over wide range of ip addresses.
# cache frequent queries using cloud front
# s3 = boto3.resource('s3')
# for bucket in s3.buckets.all():
#     print(bucket.name)
# data=open('/Users/bsudharshan/Desktop/RBTreeSampleImage.png','rb')
# s3.Bucket('file-share-test').put_object(Key='test.jpg', Body=data)
import requests
from requests_aws4auth import AWS4Auth


# {'x-amz-id-2': 'PXACG8kYbWcMje8a/07hS7Z86ASDnLbxo+RzPPYL7k0wnSZiF4Vd8mSXxhwiRnaA0EDi7225VB8=', 'x-amz-request-id': '0H4X5Q6P5X7YCSBW', 'Date': 'Fri, 03 Jul 2020 21:54:34 GMT', 'Transfer-Encoding': 'chunked', 'Server': 'AmazonS3'}

def get_token():
    # host = 'file-share-test.s3-us-west-2.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-west-2'  # e.g. us-west-1
    service = 's3'
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def initiate_mutlipart_upload():
    auth = get_token()
    response = requests.post("https://file-share-test.s3-us-west-2.amazonaws.com/example-object?uploads", auth=auth)
    print(response.status_code)
    return


initiate_mutlipart_upload()

# def get():
#         host = 'file-share-test.s3-us-west-2.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com
#     region = 'us-west-2'  # e.g. us-west-1
#
#     service = 's3'
#     credentials = boto3.Session().get_credentials()
#     awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
#
#     response = requests.get('https://file-share-test.s3-us-west-2.amazonaws.com/test.jpg',
#                             auth=awsauth)
#     print(response.status_code)

# def multi_part_upload_with_s3():
#     config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10, multipart_chunksize=1024 * 25,
#                             use_threads=True)
