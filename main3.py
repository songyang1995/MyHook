# %%
import os
from typing import Callable, Optional, Union
import PyHook3
import keyboard
import pythoncom
import win32api
import win32gui
import win32con
from ctypes import windll, byref, Structure, c_short


# noinspection PyMethodMayBeStatic
class MyHook:

    def __new__(cls, *args, **kwargs):
        cls.toggle_topmost.function_introduction = "当前窗口置顶/取消置顶"
        cls.set_bottom.function_introduction = "当前窗口置底"
        cls.toggle_window_show_hide.function_introduction = "隐藏当前窗口/显示窗口"
        cls.toggle_fullscreen.function_introduction = "当前窗口全屏/取消全屏"
        cls.toggle_lock_mousecursor.function_introduction = "锁定鼠标到当前窗口/解锁鼠标"
        cls.stop_hooking.function_introduction = "还原窗口，退出程序"
        cls.run_command.function_introduction = "运行command命令"
        return object.__new__(cls)

    def __init__(self, enable_hotkey: bool = True, enable_command: bool = True):
        # 隐藏窗口句柄
        self.status_hide_hwnd = None
        self.hook_manager: Optional[PyHook3.HookManager] = None
        # 鼠标锁定状态
        self.cursorLocked = False
        # 键: 函数 是否保留按键原功能
        self.key_func_map = {}  # {key:(func,return,args)}
        # 初始化功能键绑定
        self.config = self._get_config_from_yml()
        self._init_key_binding()
        # 初始化按键热键绑定
        if enable_hotkey:
            import keyboard
            self._init_hotkey_binding()
        if enable_command:
            self._init_command_binding()

    def _get_config_from_yml(self) -> Optional[dict]:
        import yaml
        import os
        config_path = "hotkey_map.yml"
        if os.path.isfile(config_path):
            config = yaml.safe_load(open(config_path, "r", encoding="utf8"))
            return config
        return None

    def toggle_topmost(self):
        """切换活跃窗口置顶状态"""
        hwnd = windll.user32.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST:  # 判断当前窗口是否置顶
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_SHOWWINDOW
                                  | win32con.SWP_NOMOVE
                                  | win32con.SWP_NOSIZE
                                  | win32con.SWP_NOACTIVATE
                                  )
        else:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_SHOWWINDOW
                                  | win32con.SWP_NOMOVE
                                  | win32con.SWP_NOSIZE
                                  | win32con.SWP_NOACTIVATE
                                  )

        print(title, f"置顶状态:{str(win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST)}")

    def set_bottom(self):
        """将当前窗口完全隐藏"""
        hwnd = windll.user32.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        print(title, "is bottomed")
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              # win32con.SWP_HIDEWINDOW
                              win32con.SWP_NOMOVE
                              | win32con.SWP_NOSIZE
                              | win32con.SWP_NOACTIVATE
                              )

    # noinspection DuplicatedCode
    def toggle_fullscreen(self):
        """切换窗口全屏状态，仅对WIN7以后窗口有效"""
        hwnd = windll.user32.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        print(title, "is fullScreen")
        rc = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
        # 获取之前的样式
        old_styles = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        if old_styles & win32con.WS_CAPTION != 0 and old_styles & win32con.WS_THICKFRAME != 0:
            # 有边框，删除边框
            new_styles = old_styles & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME  # 删掉old_styles 上面的WS_CAPTION和WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_styles)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, rc[2], rc[3],
                                  win32con.SWP_FRAMECHANGED)
        else:
            # 无边框，添加边框
            new_styles = old_styles | win32con.WS_CAPTION | win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_styles)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, rc[2], rc[3],
                                  win32con.SWP_FRAMECHANGED)

    def toggle_window_show_hide(self):
        """切换当前窗口显示隐藏状态，若目前有隐藏的窗口，则将隐藏窗口还原"""
        if self.status_hide_hwnd is None:
            self._hide_current_window()
        else:
            self._show_window()

    def _hide_current_window(self):
        """隐藏当前窗口，并记录窗口句柄"""
        hwnd = windll.user32.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        print(title, "is hided")
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_HIDEWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        self.status_hide_hwnd = hwnd

    def _show_window(self):
        """显示隐藏的窗口，并将隐藏窗口句柄释放"""
        hwnd = self.status_hide_hwnd
        print(win32gui.GetWindowText(hwnd), "is shown")
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                              win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        self.status_hide_hwnd = None

    class _Rect(Structure):
        _fields_ = [
            ('top', c_short),
            ('left', c_short),
            ('bottom', c_short),
            ('right', c_short)
        ]

    def toggle_lock_mousecursor(self):
        """锁定鼠标到当前窗口/解锁鼠标"""
        if self.cursorLocked:
            # 释放锁定鼠标
            windll.user32.ClipCursor(None)
            self.cursorLocked = False
        else:
            # 锁定鼠标到当前窗口
            hwnd = windll.user32.GetForegroundWindow()
            # title = win32gui.GetWindowText(hwnd)
            rect = self._Rect()
            windll.user32.GetClientRect(hwnd, byref(rect))
            windll.user32.MapWindowPoints(hwnd, None, byref(rect), 2)

            windll.user32.ClipCursor(byref(rect))
            self.cursorLocked = True
            # @https://codingdict.com/sources/py/pyglet/17307.html

    def run_command(self, command: str):
        """运行一串控制台命令"""
        return os.system(command)

    def stop_hooking(self):
        """正常退出，需还原窗口"""
        if self.status_hide_hwnd is not None:
            print("有隐藏中的窗口，准备显示")
            self._show_window()
        win32api.PostQuitMessage()
        self.hook_manager.UnhookKeyboard()
        print("卸载钩子成功，准备退出")

    def _bind_key(self, key: str, method: Callable, enable_key: bool = True, args: Union[tuple, str] = None):
        self.key_func_map[key] = (method, enable_key, args)

    def _init_key_binding(self):
        self._bind_key("F3", self.toggle_window_show_hide, False)
        self._bind_key("F4", self.toggle_window_show_hide, True)
        self._bind_key("Pause", self.toggle_topmost, False)
        self._bind_key("F5", self.toggle_fullscreen, True)
        self._bind_key("F6", self.toggle_lock_mousecursor, True)
        self._bind_key("Snapshot", self.stop_hooking, True)

    def _init_hotkey_binding(self):
        if self.config and self.config["hotkey_binding"]:
            hotkey_map: dict = self.config["hotkey_binding"]
            for old_key in hotkey_map:
                new_key = hotkey_map[old_key]
                self._bind_key(old_key, keyboard.send, False, new_key.lower())

    def _init_command_binding(self):
        if self.config and self.config["command_binding"]:
            command_map: dict = self.config["command_binding"]
            for key in command_map:
                self._bind_key(key, self.run_command, False, command_map[key])

    def repr_keybinding(self) -> str:
        keybind_str = "made by SY\nkey Mapping{\n"
        for key in self.key_func_map:
            method, enable_key, args = self.key_func_map[key]
            method: Callable
            if "function_introduction" in method.__dict__:
                method_str = method.__dict__["function_introduction"]
            else:
                method_str = f"{method}"

            keybind_str += f"  {key:<10} -> {method_str:　<20}, {'保留按键' if enable_key else '不保留按键'}, {f'[{args}]' if args else ''}\n"

        keybind_str += "}"
        return keybind_str

    def onKeyboardEvent(self, event: PyHook3.KeyboardEvent):
        # from objprint import op
        # op(event)
        if event.Key in self.key_func_map and not event.Injected:  # 该按键已被监听且是原生键盘事件
            func, enable_key, args = self.key_func_map[event.Key]
            if args and isinstance(args, tuple):
                func(*args)
            elif args and isinstance(args, str):
                func(args)
            else:
                func()
            return enable_key
        return True

    def start_hooking(self):
        # 创建一个钩子“管理对象
        self.hook_manager = PyHook3.HookManager()

        # 绑定监听函数
        self.hook_manager.KeyDown = self.onKeyboardEvent
        # 设置键盘钩子
        self.hook_manager.HookKeyboard()
        # 循环监听
        # win32gui.PumpMessages()
        pythoncom.PumpMessages()


# %%
def main():
    my_hook = MyHook(enable_hotkey=False)
    print(my_hook.repr_keybinding())
    my_hook.start_hooking()


if __name__ == "__main__":
    main()
