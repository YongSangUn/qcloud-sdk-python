# -*- coding: utf-8 -*-
import sys

from qcloud_sdk.qcloud_opt.as_opt import AsGroupOpt


def main(ip, insType, site, maxSize=20, bindingClb=True):
    """伸缩相关操作
    创建函数
    """
    opt = AsGroupOpt(ip)
    asGroupId = opt.createDefaultAsGroup(insType, site, int(maxSize),
                                         bindingClb)
    return asGroupId


if __name__ == "__main__":
    ip, insType, site, maxSize, = sys.argv[1:5]
    bindingClb = True
    main(ip, insType, site, maxSize, bindingClb)
