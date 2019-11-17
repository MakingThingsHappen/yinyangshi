# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import win32gui
import os
import time
import logging
import settings
from abc import ABCMeta, abstractmethod
from collections import Iterable
from enum import Enum
from win_tools import WindowsTools

from win_tools import MouseTools
from image_tools import ImageLocation

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class BaseRCProcessor(object):
    __metaclass__ = ABCMeta
    img_tools = ImageLocation()
    w_tools = WindowsTools()
    name = None
    ACTION_TEMP_PATH = os.path.join(BASE_DIR, 'Processor')

    def __new__(cls, *args, **kwargs):
        """单例"""
        ins = getattr(cls, '_ins', None)
        if not ins:
            ins = super(BaseRCProcessor, cls).__new__(cls, *args, **kwargs)
            setattr(cls, '_ins', ins)
            if not os.path.exists(cls.ACTION_TEMP_PATH):
                os.mkdir(cls.ACTION_TEMP_PATH)
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
        assert isinstance(self.rc(), (str,))
        self.get_location(source, self.rc())

    def click(self, pw, source, path):
        x, y, w, h = self.get_location(source, path)
        pos_x, pos_y = pw[0] + x + w // 2, pw[1] + y + h // 2
        MouseTools.setCursorPos((pos_x, pos_y))
        MouseTools.clickLeftCur()
        return True

    def action(self, hwnd, source, *args, **kwargs):
        pw = win32gui.GetWindowRect(hwnd)
        return self.click(pw, source, self.rc())


class STATE(Enum):
    UNKNOWN = 0
    START_PAGE = 1
    ZUDUI_YUHUN = 2


class StateRCProcessor(BaseRCProcessor):
    """基本状态类, 用户判断当前所处状态"""
    state = STATE.UNKNOWN

    def rc(self):
        return []

    def match(self, source):
        rcs = self.rc()
        assert isinstance(rcs, (Iterable,))
        match_list = [ImageLocation.is_match_template(source, rc) for rc in rcs]
        logging.info("StateRCProcessor match info: {}".format(match_list))
        assert all(match_list)

    @abstractmethod
    def action_rc(self):
        raise NotImplemented

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class StateOrProcessor(StateRCProcessor):
    def match(self, source):
        rcs = self.rc()
        assert isinstance(rcs, (Iterable,))
        match_list = [ImageLocation.is_match_template(source, rc) for rc in rcs]
        logging.info("StateRCProcessor match info: {}".format(match_list))
        assert any(match_list)

    def action_rc(self):
        return None


class StartPageProcessor(StateRCProcessor):
    """判断当前是否处于阴阳师主界面"""
    name = '阴阳师主界面'
    state = STATE.START_PAGE

    def rc(self):
        return [
            os.path.join(settings.RC_PATH, "ting_zhong.png"),
            os.path.join(settings.RC_PATH, "tan_suo.png")
        ]

    # TODO: 目前只处理组逻辑
    def action(self, hwnd, source, *args, **kwargs):
        """组队"""
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, self.action_rc)
        pos_x = pw[0] + x + w // 2
        pos_y = pw[1] + y + h // 2
        MouseTools.setCursorPos((pos_x, pos_y))
        MouseTools.clickLeftCur()
        self.state = STATE.ZUDUI_YUHUN
        return True

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'zu_dui.png')


class ZuDuiYuHunProcessor(StateRCProcessor):
    name = '组队/御魂页'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "zu_dui_title.png"),
            os.path.join(settings.RC_PATH, "zu_dui_yu_hun.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'zu_dui_yu_hun.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, self.action_rc)
        pos_x = pw[0] + x + w // 2
        pos_y = pw[1] + y + h // 2
        MouseTools.setCursorPos((pos_x, pos_y))
        MouseTools.clickLeftCur()
        self.state = STATE.ZUDUI_YUHUN
        return True


class ZuDuiYuHunTenProcessor(StateRCProcessor):
    name = '组队/御魂页/选择'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "zu_dui_title.png"),
            os.path.join(settings.RC_PATH, "zu_dui_yu_hun.png"),
            os.path.join(settings.RC_PATH, "zu_dui_yu_hun_ten.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'zu_dui_chuang_jian_dui_wu.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, self.action_rc)
        pos_x = pw[0] + x + w // 2
        pos_y = pw[1] + y + h // 2
        MouseTools.setCursorPos((pos_x, pos_y))
        MouseTools.clickLeftCur()
        self.state = STATE.ZUDUI_YUHUN
        return True


class ZuDuiYuHunDuiwuProcessor(StateRCProcessor):
    name = '组队/御魂页/创建队伍'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_dengji.png"),
            os.path.join(settings.RC_PATH, "yu_hun_fuben.png"),
            os.path.join(settings.RC_PATH, "yu_hun_nandu.png"),
        )

    @property
    def create_rc(self):
        return os.path.join(settings.RC_PATH, "yu_hun_duwu_create.png")

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_yiceng.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        x, y, w, h = self.get_location(source, self.action_rc)
        pos_x = pw[0] + x + w // 2
        pos_y = pw[1] + y + h // 2
        MouseTools.setCursorPos((pos_x, pos_y))
        MouseTools.clickDragDrop(0, -122)
        time.sleep(1)
        self.click(pw, source, self.create_rc)
        return True


class ZuDuiYuHunTiaozhanProcessor(StateRCProcessor):
    name = '组队/御魂页/创建队伍/挑战.'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_duiwu_title.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_duiwu_tiaozhan.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        # x, y, w, h = self.get_location(source, self.action_rc)
        # pos_x = pw[0] + x + w // 2
        # pos_y = pw[1] + y + h // 2
        # MouseTools.setCursorPos((pos_x, pos_y))
        # MouseTools.clickDragDrop(0, -125)
        # time.sleep(1)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossSetUpProcessor(StateRCProcessor):
    name = '组队/御魂页/boss/setup'

    def rc(self):
        return (
            # os.path.join(settings.RC_PATH, "yu_hun_boss_set_up_yushe.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_set_up_zu.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_setup_zhunbei.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossSetUpFinishedProcessor(StateRCProcessor):
    name = '组队/御魂页/boss/设置完成'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_set_up_zu.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_setup_finished.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_zhunbei.jpg')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        time.sleep(5)
        return True


class ZuDuiYuHunBossDoingProcessor(StateRCProcessor):
    name = '组队/御魂页/boss/进行中'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_doing.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_doing_friends.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_doing_message.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_doging_back.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_zhunbei.jpg')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        time.sleep(2)
        return True


class ZuDuiYuHunBossFinishedProcessor(StateRCProcessor):
    """御魂胜利后点击屏幕确定逻辑"""
    name = '组队/御魂页/boss/Finished'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_finished_action.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_finished_action.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossFinishedWaitProcessor(StateRCProcessor):
    """御魂胜利后等待逻辑"""
    name = '组队/御魂页/boss/FinishedWaith'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_finished_action_before.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_finished_action_before.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossFinishedType2Processor(StateRCProcessor):
    """御魂胜利后点击屏幕确定逻辑"""
    name = '组队/御魂页/boss/Finished'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_finished.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_finished.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossFinishedActionProcessor(StateRCProcessor):
    """御魂胜利后是否继续"""
    name = '组队/御魂页/boss/Finished/Retry'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_finished_retry.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_action_Yes.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, os.path.join(settings.RC_PATH, "yu_hun_boss_finished_default_select.png"))
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossFailedProcessor(StateRCProcessor):
    name = '组队/御魂页/boss/failed'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_failed.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_boss_failed.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class ZuDuiYuHunBossFailedActionProcessor(StateRCProcessor):
    name = '组队/御魂页/boss/failedAction'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "yu_hun_boss_failed.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_done.png"),
            os.path.join(settings.RC_PATH, "yu_hun_boss_failed_action.png"),
        )

    @property
    def action_rc(self):
        return os.path.join(settings.RC_PATH, 'yu_hun_action_Yes.png')

    def action(self, hwnd, source, *args, **kwargs):
        """点击御魂"""
        pw = win32gui.GetWindowRect(hwnd)
        self.click(pw, source, self.action_rc)
        return True


class TiliProcessor(BaseRCProcessor):
    """体力处理逻辑"""
    name = "tili"

    def rc(self):
        return os.path.join(settings.RC_PATH, "tl.png")


class WaitingProcessor(StateOrProcessor):
    name = '等待处理器'

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "waiting.png"),
        )

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
