#-*- coding: utf-8 -*-
"""For window procedures.
"""
import time
import ctypes
from ctypes.wintypes import RECT

from .api import (
    GetForegroundWindow,
    FindWindowEx,
    SetForegroundWindow,
    GetWindowRect,
    GW_CHILD,
    GW_ENABLEDPOPUP,
    GetWindow,
    OpenIcon,
    ShowWindow,
    SW_SHOWMAXIMIZED,
    CloseWindow,
    GetClassNameW,
    GetWindowTextW,
    SendMessageA,
    WM_CLOSE,
    MoveWindow,
    )

from .shortcut import Normalizer
from .decorator import interval
from .error import (
    Timeout,
    TooLong,
    )


TIMEOUT = 5
BUFFER_LEN = 0xFF


class Window(object):
    def __init__(self, cname=None, wname=None, hwnd=None, timeout=TIMEOUT):
        self.hwnd = hwnd
        self.cname = cname
        self.wname = wname
        self.timeout = timeout

    def set_timeout(self, value):
        self.timeout = timeout

    @staticmethod
    def get_window(cname=None, wname=None, timeout=TIMEOUT):
        timeout = TIMEOUT if timeout is None else timeout
        func = None
        args = None
        if cname == wname == None:
            func = GetForegroundWindow
            args = []
        else:
            func = FindWindowEx
            args = [None, None, cname, wname]

        count_generator = None
        if timeout == 0:
            count_generator = itertools.count
        else:
            count_generator = lambda : xrange(timeout)

        for ii in count_generator():
            try:
                hwnd = func(*args)
                if hwnd:
                    return hwnd
            except WindowsError as err:
                pass
            time.sleep(1)
        raise Timeout

    def catch(self, cname=None, wname=None, timeout=None):
        """Search window handle for cname and wname."""
        self.cname = cname
        self.wname = wname
        self.hwnd = self.get_window(cname, wname, timeout)

    @interval
    def active(self):
        SetForegroundWindow(self.hwnd)

    @interval
    def move(self, left, top):
        rect = self.get_rect(normalize=False)
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        repaint = 1
        res = MoveWindow(self.hwnd, left, top, width, height, repaint)
        return res

    def resize(self, width=None, height=None):
        rect = self.get_rect(normalize=False)
        top = rect.top
        left = rect.left
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        repaint = 1
        return MoveWindow(self.hwnd, left, top, width, height, repaint)

    def close(self):
        SendMessageA(self.hwnd, WM_CLOSE, 0, 0)

    def get_rect(self, normalize=True):
        rect = RECT()
        lprect = ctypes.pointer(rect)
        GetWindowRect(self.hwnd, lprect)
        if normalize:
            rect.left = Normalizer.xx(rect.left)
            rect.right = Normalizer.xx(rect.right)
            rect.top = Normalizer.yy(rect.top)
            rect.bottom = Normalizer.yy(rect.bottom)
        return rect

    def get_cname(self):
        for ii in range(1, 5):
            length = BUFFER_LEN * ii
            name = ctypes.create_unicode_buffer(length)
            GetClassNameW(self.hwnd, name, length)
            if len(name.value) < length:
                return name.value
        raise TooLong()

    def get_wname(self):
        for ii in range(1, 5):
            length = BUFFER_LEN * ii
            name = ctypes.create_unicode_buffer(length)
            GetWindowTextW(self.hwnd, name, length)
            if len(name.value) < length:
                return name.value
        raise TooLong()

    @property
    def width(self):
        rect = self.get_rect(normalize=False)
        return rect.right - rect.left

    @width.setter
    def width(self, value):
        self.resize(width=value)

    @property
    def height(self):
        rect = self.get_rect(normalize=False)
        return rect.bottom - rect.top

    @height.setter
    def height(self, value):
        self.resize(height=value)

    def restore(self):
        self.minimize()
        OpenIcon(self.hwnd)
        self.active()
        time.sleep(1)

    def maximize(self):
        ShowWindow(self.hwnd, SW_SHOWMAXIMIZED)
        time.sleep(1)

    def minimize(self):
        CloseWindow(self.hwnd)
        time.sleep(1)

    def get_popup(self):
        child = Window()
        child.hwnd = GetWindow(self.hwnd, GW_ENABLEDPOPUP)
        return child

    def get_child(self):
        child = Window()
        child.hwnd = GetWindow(self.hwnd, GW_CHILD)
        return child
