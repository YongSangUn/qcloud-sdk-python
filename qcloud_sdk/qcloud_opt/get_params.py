# -*- coding: utf-8 -*-

import base64

from qcloud_sdk.qcloud_modules.qcloud_cvm import QcloudCvm
from qcloud_sdk.qcloud_modules.qcloud_vpc import QcloudVpc
from qcloud_sdk.qcloud_modules.qcloud_exception import QcloudException


class GetParamsByIp(object):
    '''通过 IP 过去腾讯云像相关联的参数

    许多的参数都可以通过 IP 去匹配信息，IP 的格式为 A.B.C.D 。

    Functions:
        getServerRoom           : 获取 Ip 所属机房，通过 A.B
        getRegionAndZone        : 获取 IP 所在区域和可用区，通过 serverRoom。
        getVpcIdAndSubnetId     : 获取 IP 对应的 VpcId 和 SubnetId，通过 A.B.C
        getInsAll               : 获取实例的所有信息
        getInsId                : 获取实例 Id
    '''

    def __init__(self, ip):
        self.ip = ip
        self.serverRoom = self.getServerRoom(ip)
        self.region, self.regionZone = self.getRegionAndZone(self.serverRoom)
        self.vpcId, self.subnetId = self.getVpcIdAndSubnetId(ip)
        self.insAll = self.getInsAll(ip)

        if self.insAll is not None:
            self.insCreated = True
            self.insId = self.getInsId(ip)
            self.insName = self.getInsName(ip)
            self.insServerName = self.insName[8:]
        else:
            self.insCreated = False
            self.insId = None
            self.insName = None
            self.insServerName = None

    def getServerRoom(self, ip):
        serverRooms = {
            "AA": "xx.xx",
            "BB": "xx.xx",
        }
        for name in serverRooms.keys():
            if serverRooms[name] in ip:
                return name
        else:
            raise QcloudException("InvalidParameter", "实例所属机房不在 Qcloud，请重新选择。")

    def getRegionAndZone(self, serverRoom):
        serverRoom = self.serverRoom
        if serverRoom == "AA":
            region = "ap-xxx"
            regionZone = "ap-xxx-x"
        elif serverRoom == "BB":
            region = "ap-xxx"
            regionZone = "ap-xxx-x"
        else:
            raise QcloudException("InvalidParameterValue",
                                  "实例所属机房不在 Qcloud，请重新选择。")
        return region, regionZone

    def getVpcIdAndSubnetId(self, ip):
        vpc = QcloudVpc(self.region)
        errCode, resp = vpc.getPrivateNet(ip)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            raise QcloudException("ResourceNotFound", "No data for query.")
        else:
            vpcId = resp.SubnetSet[0].VpcId
            subnetId = resp.SubnetSet[0].SubnetId
            return vpcId, subnetId

    def getInsAll(self, ip):
        cvm = QcloudCvm(self.region)
        errCode, resp = cvm.getIns(ip)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            return None
        else:
            return resp.InstanceSet

    def getInsId(self, ip):
        insSet = self.getInsAll(ip)
        if insSet is None:
            return None
        else:
            return insSet[0].InstanceId

    def getInsName(self, ip):
        insSet = self.getInsAll(ip)
        if insSet is None:
            return None
        return insSet[0].InstanceName

    def checkInsIsCreate(self, ip):
        pass


class GetCreateParams(object):

    def __init__(self, ip, serverName, insType, image):

        self.ip = ip
        self.serverName = serverName
        self.insType = insType
        self.image = image
        # self.dataDiskSize = dataDiskSize

        self.gpbi = GetParamsByIp(ip)
        self.serverRoom = self.gpbi.serverRoom
        self.region, self.regionZone = self.gpbi.region, self.gpbi.regionZone
        self.vpcId, self.subnetId = self.gpbi.vpcId, self.gpbi.subnetId

        self.chargeType = self.getChargeType(chargeType="monthPay")
        self.insTypeId = self.getInsTypeId(insType)
        self.imgId, self.loginSet = self.getImageIdAndLoginSet(image)
        self.securityId = self.getSecurityId(self.serverRoom)
        self.hostName = self.getHostName(ip, serverName)

        self.osName = self.getOsName(self.imgId)
        self.scripts = self.getScripts(self.osName)
        self.b64Scripts = self.encodeBase64(self.scripts)

    def getChargeType(self, chargeType="monthPay"):
        chargeTypeDict = {
            "monthPay": "PREPAID",
            "hourPay": "POSTPAID_BY_HOUR",
        }
        if chargeType not in chargeTypeDict.keys():
            raise QcloudException("InvalidParameterValue", "未知的实例付费类型.")
        return chargeTypeDict[chargeType]

    def getInsTypeId(self, insType):
        '''
        参数格式为 <核心数u内存g>，例：
            insType = "4u8g"
            cpu 4 核, 内存 8 GB.
        '''

        cpuCore = insType.split("u")[0]
        ram = insType.split("u")[1].split('g')[0]
        coreCoreList = {
            "1": "SMALL",
            "2": "MEDIUM",
            "4": "LARGE",
            "8": "2XLARGE",
            "16": "4XLARGE"
        }
        # insTypeId = ("S5." + coreCoreList[cpuCore] + ram)
        insTypeId = "SA2." + coreCoreList[cpuCore] + ram
        return insTypeId

    def getSecurityId(self, serverRoom):
        if serverRoom == "AA":
            securityId = "sg-xxxxxxxx"
        elif serverRoom == "BB":
            securityId = "sg-xxxxxxxx"
        else:
            raise QcloudException("InvalidParameterValue",
                                  "所属机房不在 Qcloud，请重新选择。")
        return securityId

    def getImageIdByImgName(self, image):
        cvm = QcloudCvm(self.region)
        errCode, resq = cvm.getImg()
        if errCode is not None:
            raise Exception(resq)
        imgId = [a.ImageId for a in resq.ImageSet if a.ImageName == image]
        if imgId == []:
            raise QcloudException(
                "ResourceUnavailable",
                "在区域 " + self.region + " 中，未找到名为 " + image + " 的镜像.")
        else:
            return imgId[0]

    def getImageIdAndLoginSet(self, image):
        publicImageDict = {
            "win2016": "img-9id7emv7",
            "centos77": "img-1u6l2i9l",
            "centos76": "img-9qabwvbn",
        }

        loginSetList = [{
            "Password": "xxxxxxxx"
        }, {
            "Password": "xxxxxxxx"
        }, {
            "KeepImageLogin": "true"
        }]

        if image == "windows":
            imgId = publicImageDict["win2016"]
            loginSet = loginSetList[0]
        elif image == "linux":
            imgId = publicImageDict["centos77"]
            loginSet = loginSetList[1]

        # elif image == "windows_tmpl":
        #     imgId = self.getImageIdByImgName(image)
        #     loginSet = loginSetList[2]
        # elif image == "linux_tmpl":
        #     imgId = self.getImageIdByImgName(image)
        #     loginSet = loginSetList[2]

        elif (image.split("-")[0] == "img" and len(image.split("-")[1]) == 8):
            imgId = image
            loginSet = loginSetList[2]
        else:
            imgId = self.getImageIdByImgName(image)
            loginSet = loginSetList[2]

        return imgId, loginSet

    def getHostName(self, ip, serverName):
        serverRoom = self.serverRoom
        ip34 = "%.3d%.3d" % (int(ip.split(".")[2]), int(ip.split(".")[3]))
        hostName = serverRoom + ip34 + serverName
        return hostName

    def getOsName(self, imgId):
        cvm = QcloudCvm(self.region)
        errCode, resp = cvm.getImg(imgId)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            raise QcloudException("ResourceNotFound", "No data for query.")
        else:
            return resp.ImageSet[0].OsName

    def getScripts(self, osName):
        winScripts = '''
<powershell>
net user administrator "xxxxxxxx"
Restart-Computer -Force
</powershell>
'''
        linScripts = '''
#!/bin/bash
sed -i '/#Port 22/a Port 12345' /etc/ssh/sshd_config
service sshd restart
'''

        if "windows" in osName.lower():
            scripts = winScripts
        elif "centos" in osName.lower():
            scripts = linScripts
        else:
            scripts = 'Hello world.'

        return scripts

    def encodeBase64(self, text):
        message = text
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    def decodeBase64(self, b64Text):
        base64_message = b64Text
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return message
