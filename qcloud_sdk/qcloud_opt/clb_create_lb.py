# -*- coding: utf-8 -*-
import sys
import time

from qcloud_sdk.qcloud_modules.qcloud_clb import QcloudClb
from qcloud_sdk.qcloud_opt.get_params import GetParamsByIp


def main(vip):
    """创建指定 Vip 的负载均衡

    由于腾讯云创建负载均衡无法指定 vip , 所以写了创建指定
    Vip 的方法，但是概率太低，暂时放弃
    """
    gpbi = GetParamsByIp(vip)
    vpcId = gpbi.vpcId
    subnetId = gpbi.subnetId
    region = gpbi.region
    createNum = 20  # 创建数量

    clb = QcloudClb(region)
    errCode, resp = clb.createLb(vpcId, subnetId, createNum)
    if errCode is not None:
        print("Error: %s." % resp)
        raise Exception
    else:
        # print(resp)
        # print(type(resp))
        lbIds = resp.LoadBalancerIds
        # print(lbIds)

    errCode, resp = clb.getLb(*lbIds)
    while 0 in [lb.Status for lb in resp.LoadBalancerSet]:
        errCode, resp = clb.getLb(*lbIds)
        time.sleep(1)
    # print(resp)

    ipList = [lb.LoadBalancerVips[0] for lb in resp.LoadBalancerSet]
    print(ipList)
    if vip not in ipList:
        clb.deleteLb(*lbIds)
        main(vip)
    else:
        del lbIds[ipList.index(vip)]
        print("Delete: ")
        print(lbIds)
        clb.deleteLb(*lbIds)


if __name__ == "__main__":
    vip = sys.argv[1]
    # undone
    # main(vip)
