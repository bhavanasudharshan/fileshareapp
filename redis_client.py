import redis

__cache = redis.Redis(host='0.0.0.0', port=6379, decode_responses=True)


def get_cache():
    return __cache