# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import settings
from processor import StateRCProcessor


class FriendCloseProcessor(StateRCProcessor):
    name = "好友消息"

    def rc(self):
        return (
            os.path.join(settings.RC_PATH, "frient_send_msg_btn.png"),
            os.path.join(settings.RC_PATH, "friend_icon.png"),
        )

    def action_rc(self):
        return os.path.join(settings.RC_PATH, "friend_close_btn.png")
