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


def replay(fn: Callable) -> None:
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fn_name = fn.__qualname__
    input_key = '{}:inputs'.format(fn_name)
    output_key = '{}:outputs'.format(fn_name)
    fn_call_count = 0

    if redis_store.exists(fn_name) != 0:
        fn_call_count = int(redis_store.get(fn_name))

    print('{} was called {} times:'.format(fn_name, fn_call_count))
    fn_inputs = redis_store.lrange(input_key, 0, -1)
    fn_outputs = redis_store.lrange(output_key, 0, -1)

    for fn_input, fn_output in zip(fn_inputs, fn_outputs):
        print('{}(*{}) -> {}'.format(
            fn_name,
            fn_input.decode('utf-8'),
            fn_output,
        ))


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
