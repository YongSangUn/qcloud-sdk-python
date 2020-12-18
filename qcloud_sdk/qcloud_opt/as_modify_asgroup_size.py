# -*- coding: utf-8 -*-
import sys

from qcloud_sdk.qcloud_opt.as_opt import AsGroupOpt


def main(ip, asGroupName, desiredSize, maxSize=20):
    opt = AsGroupOpt(ip)

    asGroupName = opt.asGroupName
    asGroupId = opt.modifyAsGroupSize(asGroupName, desiredSize, maxSize)
    return asGroupId


if __name__ == "__main__":
    ip, desiredSize, maxSize = sys.argv[1:5]
    main(ip, desiredSize, maxSize)
