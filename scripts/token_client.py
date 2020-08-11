import jwt

token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1OTcxNzk0NjAsImlhdCI6MTU5NzE3ODU2MCwic3ViIjoibmNnZ3N5dmwifQ.65E8akubFG46wt39VUuLYa4twWgEzd5j6FlVXMzvvdk'
res=jwt.decode(token.encode('UTF-8'), 'SECRET', algorithm='HS256')
print(res)