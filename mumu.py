# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import os
import logging
import errors
import win32gui

from image_tools import ImageLocation
from win_tools import MouseTools, WindowsTools

logging.basicConfig(level=logging.INFO)


class Config(object):
    EMULATOR = u"MuMu模拟器"  # 所使用的模拟器名称
    RC_PATH = u"rc"  # 资源文件路径， 这个路径主要包含识别阴阳师各个部分的图片
    TEMP_PATH = u"tp"  # 截屏文件存放的位置.


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RC_PATH = os.path.join(BASE_DIR, Config.RC_PATH)


class RC(object):
    YYS_ICON = os.path.join(RC_PATH, "yys.png")
    CLOSE_ICON = os.path.join(RC_PATH, "close.png")
    WAIT2_ICON = os.path.join(RC_PATH, "wait2.png")
    WAIT3_ICON = os.path.join(RC_PATH, "wait3.png")
    WAIT5_ICON = os.path.join(RC_PATH, "wait5.png")
    JOIN_ICON = os.path.join(RC_PATH, "join.png")
    JOIN_ICON2 = os.path.join(RC_PATH, "join2.png")


class Processor(object):
    WAIT_FOR_LOAD = "wait_for_load"
    CLOSE_GAME_AD = "close_game_ad"
    UNKNOWN = "unknown"
    JOIN_GAME = "join_game"
    JOIN_GAME2 = "join_game2"


class YYSHelper(object):
    def __init__(self):
        self.img_tools = ImageLocation()  # 资源文件
        self.w_tools = WindowsTools()
        self.state = (
            (Processor.WAIT_FOR_LOAD, [RC.WAIT5_ICON, RC.WAIT2_ICON, RC.WAIT3_ICON]),
            (Processor.CLOSE_GAME_AD, RC.CLOSE_ICON),
            (Processor.UNKNOWN, ""),
            (Processor.JOIN_GAME, RC.JOIN_ICON),
            (Processor.JOIN_GAME2, RC.JOIN_ICON2),
        )

    def main(self):
        hwnd = self.find_mumu(Config.EMULATOR)
        start = self.start_yys_hw(hwnd)
        assert start is True
        time.sleep(10)
        source = self.w_tools.window_capture(hwnd, "startup.jpg", base_dir=Config.TEMP_PATH)
        while True:
            scenario, source = self.get_state(hwnd, source)
            logging.info("YYSHelper processor: {}".format(scenario))
            processor = getattr(self, scenario)
            r = processor(hwnd, source)
            assert r is True
            # 等待网络请求
            time.sleep(1.75)
            source = self.w_tools.window_capture(hwnd, "startup.jpg", base_dir=Config.TEMP_PATH)

    def unknown(self, hwnd, *args, **kwargs):
        time.sleep(2)
        source = self.w_tools.window_capture(hwnd, "unknown.jpg", base_dir=Config.TEMP_PATH)
        scenario, _ = self.get_state(hwnd, source)
        if scenario == Processor.UNKNOWN:
            raise errors.LogicNotHaveProcessor
        return True

    def get_state(self, hwnd, source, *args, **kwargs):
        for k, v in self.state:
            try:
                if isinstance(v, (str, unicode)):
                    self.get_location(source, v)
                    return k, source
                for vi in v:
                    self.get_location(source, vi)
                    return k, source
            except errors.LocationDoesNotFound:
                logging.info("LocationDoesNotFound")
                # 得到图片的颜色占比,
                radio = self.img_tools.get_color_mean(source, (0, 0, 0), 10)
                # 如果颜色占比大于80%， 则说明是纯色， 需要等待
                if radio > 0.8:
                    return Processor.WAIT_FOR_LOAD, source
                continue

        # 保存新状态到RC中，以便之后处理.
        source = self.w_tools.window_capture(hwnd, "unknown.jpg", base_dir=Config.RC_PATH)
        return Processor.UNKNOWN, source

    def wait_for_load(self, hwnd, source, *args, **kwargs):
        time.sleep(5)
        # 定位到阴阳师.
        x, y, x2, y2 = win32gui.GetWindowRect(hwnd)
        w = x2 - x + 1
        h = y2 - y + 1
        logging.info("wait_for_load: x:{}, y:{}, w:{}, h:{}".format(x, y, w, h))
        MouseTools.setCursorPos([x + w / 2, y + h / 2])
        # 启动阴阳师
        MouseTools.clickLeftCur()
        return True

    def start_yys_hw(self, hwnd):
        """启动阴阳师， 返回hwnd

        :param hwnd:
        :return:
        """
        start = False
        try:
            win32gui.SetForegroundWindow(hwnd)
            pw = win32gui.GetWindowRect(hwnd)
            source = self.w_tools.window_capture(hwnd, "emulator.jpg", base_dir=Config.TEMP_PATH)
            x, y, w, h = self.get_location(source, RC.YYS_ICON)
            # 定位到阴阳师.
            MouseTools.setCursorPos([pw[0] + x + w / 2, pw[1] + y + h / 2])
            # 启动阴阳师
            MouseTools.clickLeftCur()
            start = True
        except errors.LocationDoesNotFound as e:
            logging.warning("未在模拟器中发现阴阳师， 请重试")
        except errors.MuMuDoesNotFound as e:
            logging.warning("未找到指定的模拟器")
        return start

    def find_mumu(self, name=u"MuMu模拟器"):
        try:
            hwnds = self.w_tools.get_hwnds()
            r = self.w_tools.get_hwnd_from_title(hwnds, name)
            return r[0]
        except Exception as e:
            raise errors.MuMuDoesNotFound

    def close_game_ad(self, hwnd, source, *args, **kwargs):
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, RC.CLOSE_ICON)
        MouseTools.setCursorPos([pw[0] + x + w / 2, pw[1] + y + h / 2])
        # close ad
        MouseTools.clickLeftCur()
        return True

    def join_game(self, hwnd, source, *args, **kwargs):
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, RC.JOIN_ICON)
        MouseTools.setCursorPos([pw[0] + x + w / 2, pw[1] + y + h / 2])
        # close ad
        MouseTools.clickLeftCur()
        return True

    # 后期都换成类， 多态实现
    def join_game2(self, hwnd, source, *args, **kwargs):
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, RC.JOIN_ICON2, 0.4)
        MouseTools.setCursorPos([pw[0] + x + w / 2, pw[1] + y + h / 2])
        # close ad
        MouseTools.clickLeftCur()
        return True

    def get_location(self, source, target, threshold=0.8):
        x, y = self.img_tools.get_location(source, target, threshold)
        w, h = self.img_tools.get_target_shape()
        return x, y, w, h

    def selec_zone(self):
        pass


if __name__ == '__main__':
    YYSHelper().main()
