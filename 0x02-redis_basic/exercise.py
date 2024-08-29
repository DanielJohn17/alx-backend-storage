#!/usr/bin/env python3
'''Module for caching data in Redis'''
import redis
import uuid
from typing import Union, Callable, Any
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
    Decorator that increments the count for
    a method call in Redis
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    '''
    Decorator that stores the history of inputs and
    outputs for a particular function in Redis.
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        input_key = '{}:inputs'.format(method.__qualname__)
        output_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, output)
        return output
    return invoker


class Cache:
    '''Class for caching data in Redis'''

    def __init__(self) -> None:
        '''Initializes the Cache class'''
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @count_calls
    @call_history
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
