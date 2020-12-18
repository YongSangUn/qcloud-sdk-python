# -*- coding: utf-8 -*-
import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from qcloud_sdk.qcloud_modules.qcloud import SetQcloudBasicConfig


class QcloudCvm(SetQcloudBasicConfig):
    '''腾讯云 CVM 相关操作

    云服务器 接口，包括创建重启实例等...

    Functions：
        getIns              : 获取实例数据
        retartIns           : 重启实例
        createIns           : 创建实例
        createImg           : 通过实例创建镜像
    '''

    def __init__(self, region):
        SetQcloudBasicConfig.__init__(self, "cvm", region)

    def startJob(self, action, params):
        try:
            actionReq = action + "Request"
            req = getattr(self.models, actionReq)()
            paramsStr = json.dumps(params)
            req.from_json_string(paramsStr)
            resp = getattr(self.client, action)(req)
            return None, resp
        except TencentCloudSDKException as err:
            return err.code, err

    def getIns(self, ip="all"):
        action = "DescribeInstances"
        if ip == "all":
            params = '{}'
        else:
            params = {
                "Filters": [{
                    "Name": "private-ip-address",
                    "Values": [ip]
                }],
            }
        return self.startJob(action, params)

    def restartIns(self, instanceId):
        action = "RebootInstances"
        params = {
            "InstanceIds": [instanceId],
        }
        return self.startJob(action, params)

    def createIns(self, chargeType, regionZone, vpcId, subnetId, ip, insTypeId,
                  imgId, dataDiskSize, securityId, loginSet, hostName,
                  b64Scripts):
        insName = hostName
        action = "RunInstances"

        params = {
            "InstanceChargeType": chargeType,
            "InstanceChargePrepaid": {
                "Period": 1,
                "RenewFlag": "NOTIFY_AND_AUTO_RENEW"
            },
            "Placement": {
                "Zone": regionZone,
                "ProjectId": 1147380
            },
            "VirtualPrivateCloud": {
                "VpcId": vpcId,
                "SubnetId": subnetId,
                "PrivateIpAddresses": [ip]
            },
            "InstanceType": insTypeId,
            "ImageId": imgId,
            "SystemDisk": {
                "DiskSize": 100,
                "DiskType": "CLOUD_PREMIUM"
            },
            "DataDisks": [{
                "DiskSize": dataDiskSize,
                "DiskType": "CLOUD_PREMIUM",
                "DeleteWithInstance": True
            }],
            "SecurityGroupIds": [securityId],
            "InternetAccessible": {
                "InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 10,
                "PublicIpAssigned": False
            },
            "InstanceName": insName,
            "LoginSettings": loginSet,
            "HostName": hostName,
            "UserData": b64Scripts
        }

        return self.startJob(action, params)

    def deleteIns(self, *insIds):
        action = "TerminateInstances"
        params = {
            "InstanceIds": insIds,
        }
        return self.startJob(action, params)

    def createImg(self, insId, imgName):
        action = "CreateImage"
        params = {
            "InstanceId": insId,
            "ImageName": imgName,
        }
        return self.startJob(action, params)

    def getImg(self, *imgIds):
        action = "DescribeImages"
        if imgIds == ():
            params = {
                "Limit": 100,
            }
        else:
            params = {
                "ImageIds": imgIds,
                "Limit": 100,
            }
        return self.startJob(action, params)

    def getPrivateImg(self, *imgIds):
        action = "DescribeImages"

        if imgIds == ():
            params = {
                "Filters": [{
                    "Name": "image-type",
                    "Values": ["PRIVATE_IMAGE"]
                }]
            }
        else:
            params = {
                "ImageIds": imgIds,
            }

        return self.startJob(action, params)

    def DeleteImg(self, *imgIds):
        action = "DeleteImages"
        params = {"ImageIds": imgIds}
        return self.startJob(action, params)
