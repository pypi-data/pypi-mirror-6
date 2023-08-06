#-*- coding: utf-8 -*-
"""For clipboard.
"""
import ctypes
from .api import (
    HWND,
    GlobalLock,
    OpenClipboard,
    GetClipboardData,
    CF_UNICODETEXT,
    GlobalUnlock,
    CloseClipboard,
    GlobalAlloc,
    GMEM_DDESHARE,
    GHND,
    wcscpy_s,
    EmptyClipboard,
    SetClipboardData,
    CF_TEXT,
    )
from .decorator import interval


def _get_unicode_as_globaldata(data):
    org_restype = GlobalLock.restype
    hdata = None
    try:
        length = len(data)
        hdata = GlobalAlloc(GMEM_DDESHARE|GHND, length+1)
        ptr = GlobalLock(hdata)
        try:
            wcscpy_s(ctypes.c_wchar_p(ptr), length, data)
        finally:
            GlobalUnlock(hdata)
    finally:
        GlobalLock.restype = org_restype
    return hdata

class Clipboard(object):
    """Control clipboard."""

    @staticmethod
    def set(data):
        """Copy a data to clipboard."""
        hdata = _get_unicode_as_globaldata(data)
        OpenClipboard(None)
        try:
            EmptyClipboard()
            SetClipboardData(CF_TEXT, hdata)
        finally:
            CloseClipboard()

    @staticmethod
    def get(hwnd=None):
        """Get a clipboard data."""
        res = None
        if hwnd is None:
            hwnd = HWND(0)

        org_restype = GlobalLock.restype

        OpenClipboard(hwnd)
        try:
            hmem = GetClipboardData(CF_UNICODETEXT)
            GlobalLock.restype = ctypes.c_wchar_p
            try:
                res = GlobalLock(ctypes.c_int(hmem)) # return unicode text
            finally:
                GlobalUnlock(hmem)
        finally:
            GlobalLock.restype = org_restype
            CloseClipboard()
        return  res
