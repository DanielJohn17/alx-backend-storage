#!/usr/bin/env python3
'''Module for caching data in Redis'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    '''Decorator that caches the result of a method in Redis'''
    @wraps(method)
    def invoker(url):
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url):
    '''Gets the content of a web page'''
    return requests.get(url).text
