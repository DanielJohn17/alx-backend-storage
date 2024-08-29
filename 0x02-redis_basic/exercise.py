#!/usr/bin/env python3
'''Module for caching data in Redis'''
import redis
import uuid
from typing import Union


class Cache:
    '''Class for caching data in Redis'''

    def __init__(self) -> None:
        '''Initializes the Cache class'''
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores data in Redis and returns a key'''
        key = str(uuid.uuid4())
        self._redis.set(key, data)

        return key
