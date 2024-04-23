from ctypes import windll, byref, Structure, c_short
import win32gui
import win32con

from .base_feature import BaseFeature, SingletonFeature


class ToggleWindowTopmost(BaseFeature, SingletonFeature):
    def __call__(self):
        """切换活跃窗口置顶状态"""
        hwnd = windll.user32.GetForegroundWindow()
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

    def get_description(self):
        return "当前窗口置顶/取消置顶"


class SetWindowBottom(BaseFeature, SingletonFeature):
    def __call__(self):
        """将当前窗口完全隐藏"""
        hwnd = windll.user32.GetForegroundWindow()
        # print(win32gui.GetWindowText(hwnd), "is bottomed")
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              # win32con.SWP_HIDEWINDOW
                              win32con.SWP_NOMOVE
                              | win32con.SWP_NOSIZE
                              | win32con.SWP_NOACTIVATE
                              )

    def get_description(self):
        return "将当前窗口完全隐藏"


class ToggleWindowShowHide(BaseFeature, SingletonFeature):
    def __init__(self):
        self.hidden_hwnd = None

    def __call__(self):
        """切换当前窗口显示隐藏状态，若目前有隐藏的窗口，则将隐藏窗口还原"""
        if self.hidden_hwnd is None:
            self.hidden_hwnd = self._hide_current_window()
        else:
            self._show_hidden_window(self.hidden_hwnd)
            self.hidden_hwnd = None

    def __del__(self):
        if self.hidden_hwnd is not None:
            self._show_hidden_window(self.hidden_hwnd)

    def get_description(self):
        return "隐藏当前窗口/显示窗口"

    @staticmethod
    def _hide_current_window():
        """隐藏当前窗口，并返回窗口句柄"""
        hwnd = windll.user32.GetForegroundWindow()
        # print(type(hwnd))
        # print(win32gui.GetWindowText(hwnd), "is hided")
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_HIDEWINDOW
                              | win32con.SWP_NOMOVE
                              | win32con.SWP_NOSIZE
                              | win32con.SWP_NOACTIVATE
                              )
        return hwnd

    @staticmethod
    def _show_hidden_window(hwnd):
        """显示隐藏的窗口"""
        # (win32gui.GetWindowText(hwnd), "is shown")
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                              win32con.SWP_SHOWWINDOW
                              | win32con.SWP_NOMOVE
                              | win32con.SWP_NOSIZE
                              )


class ToggleWindowFullScreen(BaseFeature, SingletonFeature):
    def __call__(self):
        """切换窗口全屏状态
        :TODO: 已知错误：仅对WIN7 API以后窗口有效，部分老式窗口无效
        """
        hwnd = windll.user32.GetForegroundWindow()
        # title = win32gui.GetWindowText(hwnd)
        # print(title, "is fullScreen")
        rc = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
        # 获取之前的样式
        old_styles = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if old_styles & win32con.WS_CAPTION != 0 and old_styles & win32con.WS_THICKFRAME != 0:
            # 有边框，删除边框
            new_styles = old_styles & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME  # 删掉old_styles 上面的WS_CAPTION和WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_styles)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, rc[2], rc[3], win32con.SWP_FRAMECHANGED)
        else:
            # 无边框，添加边框
            new_styles = old_styles | win32con.WS_CAPTION | win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_styles)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, rc[2], rc[3], win32con.SWP_FRAMECHANGED)

    def get_description(self):
        return "当前窗口全屏/取消全屏"


class ToggleMouseCursorLock(BaseFeature, SingletonFeature):
    class _Rect(Structure):
        """内部类，和Windows API交互，获取鼠标活动区域"""
        _fields_ = [
            ('top', c_short),
            ('left', c_short),
            ('bottom', c_short),
            ('right', c_short)
        ]

    def __init__(self):
        self.cursorLocked = False

    def __call__(self):
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
            # ref @https://codingdict.com/sources/py/pyglet/17307.html

    def get_description(self):
        return "锁定鼠标到当前窗口/解锁鼠标"
