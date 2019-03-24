# -*- coding: utf-8 -*-
import logging
import os
import win32api
import win32gui
import win32process
import win32ui
from _ctypes import Structure

import win32con
from ctypes.wintypes import (
    DWORD,
    WORD,
    RECT,
    UINT,
    ATOM
)


class MouseTools(object):
    @staticmethod
    def clickLeftCur():  # 单击
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    @staticmethod
    def setCursorPos(*args, **kwargs):  # 移动鼠标
        win32api.SetCursorPos(*args, **kwargs)

    @staticmethod
    def getCurPos():  # 获得鼠标位置信息，这个再实际代码没用上，调试用得上
        return win32gui.GetCursorPos()


class WindowsTools(object):
    @staticmethod
    def get_hwnds():
        """return a list of window handlers based on it process id"""

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    @staticmethod
    def get_hwnd_from_title(hwnds, title):
        return filter(lambda i: title in win32gui.GetWindowText(i).decode("gb2312"), hwnds)

    @staticmethod
    def window_capture(hwnd, filename="capture.jpg", base_dir="rs"):
        # 获取模拟器的坐标
        x, y, x2, y2 = win32gui.GetWindowRect(hwnd)
        w = x2 - x + 1
        h = y2 - y + 1
        logging.info("window_capture: x:{}, y:{}, w:{}, h:{}".format(x, y, w, h))
        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        hwndDC = win32gui.GetWindowDC(hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()

        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        path = os.path.join(base_dir, filename)
        saveBitMap.SaveBitmapFile(saveDC, path)
        return path


class tagWINDOWINFO(Structure):

    def __str__(self):
        return '\n'.join([key + ':' + str(getattr(self, key)) for key, value in self._fields_])


tagWINDOWINFO._fields_ = [
    ('cbSize', DWORD),
    ('rcWindow', RECT),
    ('rcClient', RECT),
    ('dwStyle', DWORD),
    ('dwExStyle', DWORD),
    ('dwWindowStatus', DWORD),
    ('cxWindowBorders', UINT),
    ('cyWindowBorders', UINT),
    ('atomWindowType', ATOM),
    ('wCreatorVersion', WORD),
]

WINDOWINFO = tagWINDOWINFO
