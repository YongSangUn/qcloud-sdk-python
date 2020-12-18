# -*- coding: utf-8 -*-
import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from qcloud_sdk.qcloud_modules.qcloud import SetQcloudBasicConfig


class QcloudClb(SetQcloudBasicConfig):
    '''腾讯云 CLB 相关操作

    负载均衡相关操作，非传统性的负载均衡。包括监听器、目标组的相关的操作。

    Functions:
        getLb                   : get LoadBalancers，获取负载均衡列表
        getLbByIp               : 通过绑定的后端服务 IP 查询负载均衡
        getLbl                  : get loadBalance listeners, 获取负载均衡监听器列表
        getInsFromLb            : 查询负载均衡绑定的后端服务列表
        addInsToListener        : 绑定后端服务到监听器
        delInsFromListener      : 从监听器解绑后端服务
        modifyWeight            : 修改监听器中后端服务的转发权重

    '''

    def __init__(self, region):
        SetQcloudBasicConfig.__init__(self, "clb", region)

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

    def getLb(self, *lbIds):
        action = "DescribeLoadBalancers"
        if lbIds:
            params = {"LoadBalancerIds": lbIds}
        else:
            params = {"Limit": 100}
        return self.startJob(action, params)

    def getLbByIp(self, *ip):
        # ipList = tuple(ip)
        action = "DescribeLoadBalancers"
        params = {
            "BackendPrivateIps": ip,
        }
        return self.startJob(action, params)

    def getLbl(self, loadBalancerId, listenerId=""):
        action = "DescribeListeners"
        params = {"LoadBalancerId": loadBalancerId, "ListenerId": [listenerId]}
        return self.startJob(action, params)

    def getInsFromLb(self, loadBalancerId, listenerId=""):
        action = "DescribeTargets"
        params = {"LoadBalancerId": loadBalancerId, "ListenerId": [listenerId]}
        return self.startJob(action, params)

    # 暂时搁置，参数较为复杂，需求不大。
    def createRule(self, loadBalancerId, listenerId, siteName, heartbeat):
        action = "CreateRule"
        params = {
            "LoadBalancerId":
                loadBalancerId,
            "ListenerId": [listenerId],
            "Rules": [{
                "Domain":
                    siteName,
                "Url":
                    "/",
                "HealthCheck": [{
                    "HealthSwitch": 1,
                    "IntervalTime": 30,
                    "HttpCode": 7,
                    "HttpCheckPath": heartbeat,
                    "HttpCheckDomain": siteName,
                    "HttpCheckMethod": ""
                }]
            }]
        }
        return self.startJob(action, params)

    def createLb(self, vpcId, subnetId, createNum=1):
        action = "CreateLoadBalancer"
        params = {
            "LoadBalancerType": "INTERNAL",
            "VpcId": vpcId,
            "SubnetId": subnetId,
            "Number": int(createNum)
        }
        return self.startJob(action, params)

    def deleteLb(self, *lbIds):
        action = "DeleteLoadBalancer"
        params = {"LoadBalancerIds": lbIds}
        return self.startJob(action, params)

    def addInsToListener(self, loadBalancerId, listenerId, siteName, *insId):
        '''绑定后端服务到监听器

        需要传入监听器所在 LB 和 监听器本身的 ID 、站点名称、以及需要绑定的实例 ID。

        Args：
            loadBalancerId      : 负载均衡 ID。
            listenerId          : 监听器 ID。
            siteName            : 监听器中站点的名称，也是规则中的站点名。
            insId               : 实例Id，当只有一个时，需要转换成元组。
            targetsList         : array，内容是传入实例的列表。每个实例通过字典存储信息。
                                  所以是由字典为元素的数组。
        '''

        # 遍历 insId 生成 targetsList 数组。
        targetsList = []
        insIds = insId
        # insIds = tuple(insId)
        for ins in insIds:
            insDict = {"InstanceId": ins, "Port": 80, "Weight": 10}
            targetsList.append(insDict)

        action = "RegisterTargets"
        params = {
            "LoadBalancerId": loadBalancerId,
            "ListenerId": listenerId,
            "Domain": siteName,
            "Url": "/",
            "Targets": targetsList
        }
        return self.startJob(action, params)

    def delInsFromListener(self, loadBalancerId, listenerId, siteName, *insId):
        '''从监听器解绑后端服务

        需要传入监听器所在 LB 和 监听器本身的 ID 、站点名称、以及需要解绑的实例 ID。

        Args：
            loadBalancerId      : 负载均衡 ID。
            listenerId          : 监听器 ID。
            siteName            : 监听器中站点的名称，也是规则中的站点名。
            insId               : 实例Id，当只有一个时，需要转换成元组。
            targetsList         : array，内容是传入实例的列表。每个实例通过字典存储信息。
                                  所以是由字典为元素的数组。
        '''

        targetsList = []
        insIds = insId
        # insIds = tuple(insId)
        for ins in insIds:
            insDict = {"InstanceId": ins, "Port": 80, "Weight": 10}
            targetsList.append(insDict)

        action = "DeregisterTargets"
        params = {
            "LoadBalancerId": loadBalancerId,
            "ListenerId": listenerId,
            "Domain": siteName,
            "Url": "/",
            "Targets": targetsList
        }
        return self.startJob(action, params)

    def modifyWeight(self, loadBalancerId, listenerId, siteName, weight,
                     *insId):
        '''修改监听器中后端服务的转发权重

        权重可以指定全局也可以在实例的 targetsList 中指定，但是targetsList 中指定后，全局的不生效，
        这里是写在实例字典中。

        Args：
            loadBalancerId      : 负载均衡 ID。
            listenerId          : 监听器 ID。
            siteName            : 监听器中站点的名称，也是规则中的站点名。
            insId               : 实例Id，当只有一个时，需要转换成元组。
            targetsList         : array，内容是传入实例的列表。每个实例通过字典存储信息。
                                  所以是由字典为元素的数组。
        '''

        targetsList = []
        insIds = insId
        # insIds = tuple(insId)
        for ins in insIds:
            insDict = {"InstanceId": ins, "Port": 80}
            targetsList.append(insDict)

        action = "ModifyTargetWeight"
        params = {
            "LoadBalancerId": loadBalancerId,
            "ListenerId": listenerId,
            "Domain": siteName,
            "Url": "/",
            "Weight": weight,
            "Targets": targetsList
        }
        return self.startJob(action, params)
