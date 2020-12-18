# -*- coding: utf-8 -*-

import sys
import json
import time

from qcloud_sdk.qcloud_modules.qcloud_clb import QcloudClb
from qcloud_sdk.qcloud_opt.get_params import GetParamsByIp


class ModifyWeight(GetParamsByIp):
    '''修改监听器绑定实例的转发权重

    '''

    def __init__(self, ip):
        self.ip = ip
        GetParamsByIp.__init__(self, ip)
        self.clb = QcloudClb(self.region)

    def getLbId(self, ip):
        reqDict = json.loads(self.clb.getLbByIp(ip))
        # totalNum = reqDict["TotalCount"]
        lbList = reqDict["LoadBalancerSet"]
        lbId = []
        for lb in lbList:
            lbId.append(lb["LoadBalancerId"])
        return tuple(lbId)

    def getLblInsList(self, lb, listenId, site):
        reqDict = json.loads(self.clb.getInsFromLb(lb, listenId))
        rules = reqDict["Listeners"][0]["Rules"]
        for rule in rules:
            domain = rule["Domain"]
            # 列表生成式 生成 insList
            insList = [ip["InstanceId"] for ip in rule["Targets"]]
            weightList = [
                ip["InstanceId"] + "  weight: " + str(ip["Weight"])
                for ip in rule["Targets"]
            ]
            if site == domain:
                print("  -- The status of the instance and its weight:")
                print("    " + str(weightList))
                return tuple(insList)

    def modify(self, lb, listenId, site, weight, insId):
        insList = self.getLblInsList(lb, listenId, site)
        if insId in insList:
            for i in range(1, 6):
                req = self.clb.modifyWeight(lb, listenId, site, weight, insId)
                if isinstance(req, str):
                    print("  -- Request successful.\n    ", req)
                    break
                else:
                    time.sleep(3)
                    print("  -- Request to retry...")
            else:
                raise TypeError(
                    "  -- Request failed, plz check the incoming parameters")
        else:
            raise TypeError(" -- 监听器中未找到指定 IP。")

    def startWork(self, site, weight, ip):
        insId = self.getInsId(ip)  # 继承 GetParamsByIp 类中方法，通过 ip 获取 insId
        lbId = self.getLbId(ip)
        print(">> Ip matching loadbalance list:\n    " + str(lbId) + "\n")
        for lb in lbId:
            reqDict = json.loads(self.clb.getLbl(lb))
            listeners = reqDict["Listeners"]
            for listen in listeners:
                listenName = listen["ListenerName"]
                listenId = listen["ListenerId"]
                rules = listen["Rules"]
                if rules is None:
                    print("==> " + listenName + " 没有规则，跳过。")
                    break
                for rule in rules:
                    domain = rule["Domain"]
                    # locId = rule["LocationId"]
                    if site == domain:
                        # print(site, domain)
                        # print(lb, listenId, site, weight, insIds)
                        # time.sleep(10)
                        print("==> %-25s %-25s Weight: %s" %
                              (listenName, domain, weight))
                        self.modify(lb, listenId, site, weight, insId)


if __name__ == "__main__":
    ip, site, weight = sys.argv[1:4]
    mw = ModifyWeight(ip)
    mw.startWork(site, weight, ip)
