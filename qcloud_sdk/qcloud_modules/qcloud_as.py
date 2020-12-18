# -*- coding: utf-8 -*-
import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from qcloud_sdk.qcloud_modules.qcloud import SetQcloudBasicConfig


class QcloudAs(SetQcloudBasicConfig):
    '''腾讯云 AS 相关接口

    AS (auto scaling) 自动扩容，包括启动配置和伸缩组相关操作。

    functions:
        createLaunch              : 创建启动配置
        getLaunch                 : 通过名字查询启动配置
        deleteLaunch              : 通过启动配置 ID 删除启动配置
        createAsGroup             : 创建伸缩组
        getAsGroup                : 通过名字查询伸缩组
        modifyAsGroup             : 修改伸缩组，目前只有最大值和期望值
        deleteAsGroup             : 删除伸缩组
    '''

    def __init__(self, region):
        SetQcloudBasicConfig.__init__(self, "as", region)

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

    def createLaunch(self, launchName, imgId, insTypeId):
        action = "CreateLaunchConfiguration"
        params = {
            "LaunchConfigurationName": launchName,
            "ImageId": imgId,
            "InstanceType": insTypeId,
            "SystemDisk": {
                "DiskType": "CLOUD_PREMIUM",
                "DiskSize": 100
            },
            "InternetAccessible": {
                "InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 10,
                "PublicIpAssigned": False
            },
            "LoginSettings": {
                "KeepImageLogin": True
            }
        }
        return self.startJob(action, params)

    def getLaunch(self, *launchNames):
        action = "DescribeLaunchConfigurations"
        params = {
            "Filters": [{
                "Name": "launch-configuration-name",
                "Values": launchNames
            }]
        }
        return self.startJob(action, params)

    def modifyLaunchImgId(self, launchId, imgId):
        action = "ModifyLaunchConfigurationAttributes"
        params = {"LaunchConfigurationId": launchId, "ImageId": imgId}
        return self.startJob(action, params)

    def deleteLaunch(self, launchId):
        action = "DeleteLaunchConfiguration"
        params = {
            "LaunchConfigurationId": launchId,
        }
        return self.startJob(action, params)

    def createAsGroup(self, asGroupName, launchId, maxSize, vpcId, subnetId,
                      forwardLbs):
        '''
        forwardLbs(list)            : 应用负载均衡的参数，包括负载均衡、监听器、
                                      和域名 ID 的集合。
        '''
        action = "CreateAutoScalingGroup"
        params = {
            "AutoScalingGroupName": asGroupName,
            "LaunchConfigurationId": launchId,
            "MaxSize": maxSize,
            "MinSize": 0,
            "DesiredCapacity": 0,
            "VpcId": vpcId,
            "SubnetIds": [subnetId],
            "ForwardLoadBalancers": forwardLbs,
        }
        return self.startJob(action, params)

    def getAsGroup(self, *asGroupNames):
        action = "DescribeAutoScalingGroups"
        params = {
            "Filters": [{
                "Name": "auto-scaling-group-name",
                "Values": asGroupNames
            }]
        }
        return self.startJob(action, params)

    def modifyAsGroup(self, asGroupId, desiredSize, maxSize):
        action = "ModifyAutoScalingGroup"
        params = {
            "AutoScalingGroupId": asGroupId,
            "DesiredCapacity": desiredSize,
            "MaxSize": maxSize
        }
        return self.startJob(action, params)

    def deleteAsGroup(self, asGroupId):
        action = "DeleteAutoScalingGroup"
        params = {
            "AutoScalingGroupId": asGroupId,
        }
        return self.startJob(action, params)
