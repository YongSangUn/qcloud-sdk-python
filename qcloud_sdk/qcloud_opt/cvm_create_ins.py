# -*- coding: utf-8 -*-
import sys

from qcloud_sdk.qcloud_modules.qcloud_cvm import QcloudCvm
from qcloud_sdk.qcloud_modules.qcloud_clb import QcloudClb
from qcloud_sdk.qcloud_opt.get_params import GetCreateParams
from qcloud_sdk.qcloud_modules.qcloud_exception import QcloudException


class RunInstances(GetCreateParams):

    def __init__(self, ip, serverName, insType, image, dataDiskSize=0):
        """
        """
        self.dataDiskSize = dataDiskSize

        # 这里的 IP 作为判断实例参数的依据
        GetCreateParams.__init__(self, ip, serverName, insType, image)

    def getLbVipList(self):
        clbClient = QcloudClb(self.region)
        errCode, resp = clbClient.getLb()
        # 注意 lb.LoadBalancerVips 是一个列表, 所以需要新建空列表相加。
        lbVipList = []
        for lb in resp.LoadBalancerSet:
            lbVipList += lb.LoadBalancerVips
        return lbVipList

    def checkIpIsLbVip(self, ip):
        lbVipList = self.getLbVipList()
        if ip in lbVipList:
            return True
        else:
            return False

    def checkForInsExisted(self, ip):
        if not self.checkIpIsLbVip(ip) and self.gpbi.getInsId(ip) is None:
            return False
        else:
            return True

    def createIns(self, ip):
        if not self.checkForInsExisted(ip):
            chargeType = self.chargeType
            regionZone = self.regionZone
            vpcId, subnetId = self.vpcId, self.subnetId
            insTypeId = self.insTypeId
            imgId = self.imgId
            securityId = self.securityId
            dataDiskSize = self.dataDiskSize
            loginSet = self.loginSet
            b64Scripts = self.b64Scripts

            # hostName = self.hostName
            # 注意 每一台的主机名 都不一样
            hostName = self.getHostName(ip, self.serverName)

            cvmClient = QcloudCvm(self.region)
            errCode, resp = cvmClient.createIns(chargeType, regionZone, vpcId,
                                                subnetId, ip, insTypeId, imgId,
                                                dataDiskSize, securityId,
                                                loginSet, hostName, b64Scripts)
            if errCode is not None:
                raise Exception(resp)
            else:
                return resp
        else:
            raise QcloudException(
                "ResourceInUse",
                "The instance of " + ip + " is already existed.")

    def multCreateIns(self, *ips):
        checkDone = True
        for ip in ips:
            if not self.checkForInsExisted(ip):
                pass
            else:
                print("Instance check error: " + ip)
                checkDone = False

        if checkDone:
            for ip in ips:
                print(self.createIns(ip))
        else:
            raise QcloudException("FailedOperation",
                                  "Checking for IP occupancy errors.")


if __name__ == "__main__":
    serverName, insType, image, dataDiskSize, *ips = sys.argv[1:]
    mainIp = ips[0]
    run = RunInstances(mainIp, serverName, insType, image, dataDiskSize)
    run.multCreateIns(*ips)