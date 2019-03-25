# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import win32gui
import os
import time
import logging
import settings
from abc import ABCMeta, abstractmethod

from win_tools import MouseTools
from image_tools import ImageLocation

logging.basicConfig(level=logging.INFO)


class BaseRCProcessor(object):
    __metaclass__ = ABCMeta
    img_tools = ImageLocation()
    name = None

    def __new__(cls, *args, **kwargs):
        ins = getattr(cls, '_ins', None)
        if not ins:
            ins = super(BaseRCProcessor, cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_ins', ins)
        return ins

    @abstractmethod
    def rc(self):
        raise NotImplemented

    def get_location(self, source, target, threshold=0.8):
        x, y = ImageLocation.get_location(source, target, threshold)
        w, h = ImageLocation.get_target_shape(target)
        return x, y, w, h

    def match(self, source):
        """查看是否与当前rc相符合， 符合返回loc和source 否则抛出异常"""
        assert isinstance(self.rc(), (str, unicode))
        self.get_location(source, self.rc())

    def action(self, hwnd, source, *args, **kwargs):
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, self.rc())

        MouseTools.setCursorPos([pw[0] + x + w / 2, pw[1] + y + h / 2])
        MouseTools.clickLeftCur()
        return True


class TiliProcessor(BaseRCProcessor):
    """体力处理逻辑"""
    name = "tili"

    def rc(self):
        return os.path.join(settings.RC_PATH, "tl.png")


class WaitProcessor(BaseRCProcessor):
    name = 'wait'

    def rc(self):
        return [
            os.path.join(settings.RC_PATH, "wait5.png"),
            os.path.join(settings.RC_PATH, "wait2.png"),
            os.path.join(settings.RC_PATH, "wait3.png"),
        ]

    def match(self, source):
        for vi in self.rc():
            self.get_location(source, vi)
            return self.name, source

    def action(self, hwnd, source, *args, **kwargs):
        time.sleep(5)
        x, y, x2, y2 = win32gui.GetWindowRect(hwnd)
        w = x2 - x + 1
        h = y2 - y + 1
        logging.info("wait_for_load: x:{}, y:{}, w:{}, h:{}".format(x, y, w, h))
        # 将鼠标定位到中心位置.
        MouseTools.setCursorPos([x + w / 2, y + h / 2])
        MouseTools.clickLeftCur()
        return True


class CloseWinProcessor(BaseRCProcessor):
    """处理窗口中的X按钮"""
    name = 'close_x"'

    def rc(self):
        return os.path.join(settings.RC_PATH, "close.png")


# TODO： 后期考虑自动生成类
class JoinGameProcessor(BaseRCProcessor):
    name = 'join_game'

    def rc(self):
        return os.path.join(settings.RC_PATH, "join.png")


class JoinGame2Processor(BaseRCProcessor):
    name = 'join_game2'

    def rc(self):
        return os.path.join(settings.RC_PATH, "join2.png")
