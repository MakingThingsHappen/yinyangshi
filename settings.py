# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMULATOR = u"阴阳师-网易游戏"  # 所使用的模拟器名称
RC_PATH = os.path.join(BASE_DIR, "rc")  # 资源文件路径， 这个路径主要包含识别阴阳师各个部分的图片
TEMP_PATH = os.path.join(BASE_DIR, u"tp")  # 截屏文件存放的位置.

YYS_RC_PATH = os.path.join(RC_PATH, 'yys.png')
YYS_DOOR_PATH = os.path.join(RC_PATH, 'yys_door.png')
