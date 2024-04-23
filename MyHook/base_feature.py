import abc
import threading
import warnings
from typing import Callable


class BaseFeature(abc.ABC):
    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError

    def get_description(self):
        if self.__call__.__doc__ is not None and len(self.__call__.__doc__.strip()) > 1:
            warnings.warn("please override method get_description(self) instead of using method documentation of __call__(self)", DeprecationWarning)
            return self.__call__.__doc__
        else:
            raise NotImplementedError("please override method get_description(self) or add a method documentation to __call__(self)")


class SingletonFeature:
    # singleton class variable
    _instance_lock = threading.Lock()
    _instance_dict = dict()

    def __new__(cls, *args, **kwargs):
        """singleton __new__() method"""
        if cls.__name__ not in SingletonFeature._instance_dict:
            with SingletonFeature._instance_lock:
                _instance = super().__new__(cls, *args, **kwargs)
                SingletonFeature._instance_dict[cls.__name__] = _instance
        return SingletonFeature._instance_dict[cls.__name__]


class RunCallable(BaseFeature):
    def __init__(self, func: Callable, *args: object, **kwargs: object) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.func(*self.args, **self.kwargs)

    def get_description(self):
        return f"执行函数 {self.func.__name__},args={self.args},kwargs={self.kwargs}"
