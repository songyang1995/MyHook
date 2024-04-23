import os
from typing import Callable

from .base_feature import BaseFeature
import keyboard


class Hotkey(BaseFeature):
    """热键替换"""

    def __init__(self, new_key: str):
        # TODO:最好在这里检查一遍按键合法性
        self.new_key = new_key

    def __call__(self):
        keyboard.send(self.new_key.lower())

    def get_description(self):
        return f"替换为 {self.new_key} 键"


class RunCommand(BaseFeature):
    """运行一串控制台命令"""

    def __init__(self, command: str):
        """
        :param command: 命令行口令
        """
        self.command = command

    def __call__(self):
        return os.system(self.command)

    def get_description(self):
        return f"运行命令：{self.command}"


class RunCallable(BaseFeature):
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    def get_description(self):
        return f"执行函数 {self.func.__name__},args={self.args},kwargs={self.kwargs}"
