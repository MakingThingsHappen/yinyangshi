# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import logging
import errors
import win32gui
import processor
import processor_friends
from settings import RC_PATH, EMULATOR, TEMP_PATH, YYS_DOOR_PATH
from win_tools import WindowsTools
from image_tools import ImageLocation

logging.basicConfig(level=logging.INFO)

PROCESSOR = (
    # processor.CloseWinProcessor(),
    # processor.JoinGameProcessor(),
    # processor.JoinGame2Processor(),
    # processor.WaitProcessor(),
    processor.StartPageProcessor(),
    processor.ZuDuiYuHunTenProcessor(),
    processor.ZuDuiYuHunDuiwuProcessor(),
    processor.ZuDuiYuHunTiaozhanProcessor(),

    processor.ZuDuiYuHunBossSetUpFinishedProcessor(),
    processor.ZuDuiYuHunBossSetUpProcessor(),
    processor.ZuDuiYuHunBossFailedActionProcessor(),
    processor.ZuDuiYuHunBossFailedProcessor(),
    processor.ZuDuiYuHunBossFinishedProcessor(),
    processor.ZuDuiYuHunBossFinishedWaitProcessor(),
    processor.ZuDuiYuHunBossFinishedType2Processor(),
    processor.ZuDuiYuHunBossFinishedActionProcessor(),
    processor.ZuDuiYuHunBossDoingProcessor(),
    processor.ZuDuiYuHunProcessor(),

    # friend
    # processor_friends.FriendCloseProcessor(),
)


class YYSHelper(object):
    w_tools = WindowsTools()

    def main(self):
        hwnd = self.find_yys_destop(EMULATOR)
        start = self.focus_yys(hwnd)
        assert start is True
        source = self.w_tools.window_capture(hwnd, "startup.jpg", base_dir=TEMP_PATH)
        while True:
            p, source = self.get_state(hwnd, source)
            if isinstance(p, (processor.BaseRCProcessor,)):
                logging.info("YYSHelper processor: {}".format(p.name))
                for i in range(3):
                    try:
                        r = p.action(hwnd, source)
                        if r: break
                    except errors.LocationDoesNotFound:
                        time.sleep(1)
                        source = self.w_tools.window_capture(hwnd, "startup.jpg", base_dir=TEMP_PATH)
                        continue
            else:
                logging.info("YYSHelper unknown processor: {}".format(p))
                p = getattr(self, p)
                r = p(hwnd, source)
            assert r is True
            # 等待网络请求
            time.sleep(1.75)
            source = self.w_tools.window_capture(hwnd, "startup.jpg", base_dir=TEMP_PATH)

    def unknown(self, hwnd, *args, **kwargs):
        time.sleep(2)
        source = self.w_tools.window_capture(hwnd, "unknown.jpg", base_dir=TEMP_PATH)
        scenario, _ = self.get_state(hwnd, source)
        if scenario == "unknown":
            raise errors.LogicNotHaveProcessor
        return True

    def get_state(self, hwnd, source, *args, **kwargs):
        logging.info("====== start ======\n")
        for p in PROCESSOR:
            try:
                logging.info("当前处理器: %s", p.name)
                p.match(source)
                return p, source
            except errors.LocationDoesNotFound:
                logging.info("get_state->LocationDoesNotFound")
                # 得到图片的颜色占比,
                radio = ImageLocation.get_color_mean(source, (0, 0, 0), 10)
                # 如果颜色占比大于80%， 则说明是纯色， 需要等待
                if radio > 0.8:
                    return processor.WaitProcessor(), source
                continue
            except AssertionError:
                continue
            # except Exception as e:
            #     logging.warning("get_state: %s", str(e))

        logging.info("====== end ======\n")
        # 保存新状态到RC中，以便之后处理.
        source = self.w_tools.window_capture(hwnd, "unknown.jpg", base_dir=RC_PATH)
        return "unknown", source

    def focus_yys(self, hwnd):
        """定位到阴阳师主界面， 返回hwnd

        :param hwnd:
        :return:
        """
        start = False
        try:
            win32gui.SetForegroundWindow(hwnd)
            # pw = win32gui.GetWindowRect(hwnd)
            # source = self.w_tools.window_capture(hwnd, "emulator.jpg", base_dir=TEMP_PATH)
            # x, y, w, h = self.get_location(source, YYS_DOOR_PATH)
            # # 定位到阴阳师.
            # MouseTools.setCursorPos([pw[0] + x + w // 2, pw[1] + y + h // 2])
            # # 启动阴阳师
            # MouseTools.clickLeftCur()
            start = True
        except errors.LocationDoesNotFound as e:
            logging.warning("未在模拟器中发现阴阳师， 请重试")
        except errors.MuMuDoesNotFound as e:
            logging.warning("未找到指定的模拟器")
        return start

    def find_yys_destop(self, name=u"MuMu模拟器"):
        try:
            hwnds = self.w_tools.get_hwnds()
            r = self.w_tools.get_hwnd_from_title(hwnds, name)
            return list(r)[0]
        except Exception as e:
            raise errors.MuMuDoesNotFound

    def get_location(self, source, target, threshold=0.8):
        x, y = ImageLocation.get_location(source, target, threshold)
        w, h = ImageLocation.get_target_shape(target)
        return x, y, w, h


def get_current_status():
    """得到当前所处状态

    :return:
    """
    pass


def check_current_status():
    """检查当前状态

    :return:
    """


if __name__ == '__main__':
    YYSHelper().main()
