#!/usr/bin/env python3
'''Module for caching data in Redis'''
import redis
import uuid
from typing import Union, Callable


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

    def get(self,
            key: str,
            fn: Callable = None
            ) -> Union[str, bytes, int, float]:
        '''Gets and returns the data for the given key'''
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        '''Gets and returns the data as a string'''
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        '''Gets and returns the data as an integer'''
        return self.get(key, lambda x: int(x))
