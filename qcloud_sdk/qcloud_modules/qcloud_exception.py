# -*- coding: utf-8 -*-

import sys


class QcloudException(Exception):
    """Qcloud 异常类
    使用了和腾讯云 sdk 异常处理相同的模块。
    """

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def __str__(self):
        s = "[QcloudException] code: %s message: %s" % (self.code,
                                                        self.message)
        # 兼容 python2 ，本 sdk 基于 python3， 其实无需兼容。
        if sys.version_info[0] < 3 and isinstance(s, unicode):
            return s.encode("utf8")
        else:
            return s

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message
