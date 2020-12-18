# -*- coding:utf-8 -*-

import sys

from qcloud_sdk.qcloud_opt.as_opt import AsGroupOpt


def main(ip, launchName=None):
    """更新启动配置的镜像

    Args:
        ip (str): 用于制作镜像的实例 IPv4 地址
    """
    opt = AsGroupOpt(ip)
    if launchName is None:
        launchName = opt.launchName

    print(opt.updateLaunchImg(launchName, ip))


if __name__ == "__main__":
    ip, launchName = sys.argv[1:3]
    main(ip, launchName)
