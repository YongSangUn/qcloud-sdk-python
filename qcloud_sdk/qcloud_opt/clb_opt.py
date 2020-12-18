# -*- coding: utf-8 -*-

from qcloud_sdk.qcloud_modules.qcloud_as import QcloudAs
from qcloud_sdk.qcloud_modules.qcloud_cvm import QcloudCvm
from qcloud_sdk.qcloud_modules.qcloud_clb import QcloudClb
from qcloud_sdk.qcloud_opt.get_params import GetParamsByIp


class ClbOpt(object):
    """
    docstring
    """

    def __init__(self, region=None):
        if region is None:
            region = "ap-shanghai"
        self.clb = QcloudClb(region)

    def getIpBindingLbs(self, ip):
        errcode, resp = self.clb.getLbByIp(ip)
        if errcode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            return 0, None
        else:
            bindingLbs = {
                lb.LoadBalancerId: lb.LoadBalancerVips
                for lb in resp.LoadBalancerSet
            }
            return resp.TotalCount, bindingLbs

    def getIpBindingListenerRules(self, ip, site):
        bidingLbNum, lbs = self.getIpBindingLbs(ip)

        if bidingLbNum == 0:
            return 0, None

        bindingRules = []
        for lbId, lbVip in lbs.items():
            errcode, resp = self.clb.getLbl(lbId)
            if errcode is not None:
                raise Exception(resp)
            else:
                for listener in resp.Listeners:
                    for rule in listener.Rules:
                        if rule.Domain == site:
                            rule.LoadBalancerId = lbId
                            rule.LoadBalancerVips = lbVip

    def getListenerBindingIns(self, lb, listenerId, site):
        pass
