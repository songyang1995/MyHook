import abc
import threading
import warnings


class BaseFeature(abc.ABC):
    """Abstract class for all features"""

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError

    def get_description(self) -> str:
        if self.__call__.__doc__ is not None and len(self.__call__.__doc__.strip()) > 0:
            warnings.warn("please override method get_description(self) instead of using method documentation of __call__(self)", DeprecationWarning)
            return self.__call__.__doc__
        elif self.__class__.__doc__ is not None and len(self.__class__.__doc__.strip()) > 0:
            warnings.warn("please override method get_description(self) instead of using class documentation", DeprecationWarning)
            return self.__class__.__doc__
        else:
            raise NotImplementedError("please override method get_description(self) or add a documentation to method __call__(self)")


class Singleton:
    # class variable to implement singleton
    _instance_lock = threading.Lock()
    _instance_dict: dict[str, object] = {}

    def __new__(cls, *args, **kwargs):
        """singleton __new__() method"""
        if cls.__name__ not in Singleton._instance_dict:
            with Singleton._instance_lock:
                _instance = super().__new__(cls, *args, **kwargs)
                Singleton._instance_dict[cls.__name__] = _instance
        return Singleton._instance_dict[cls.__name__]


class TestFeature(BaseFeature):
    """test feature class doc"""

    def __call__(self):
        print("test")


if __name__ == '__main__':
    t = TestFeature()
    print(t.get_description())
