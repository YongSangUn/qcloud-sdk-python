# -*- coding: utf-8 -*-
import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from qcloud_sdk.qcloud_modules.qcloud import SetQcloudBasicConfig


class QcloudVpc(SetQcloudBasicConfig):
    '''腾讯云 VPC 相关操作

    虚拟网络 接口，包括子网、网关等操作。

    Functions:
        getPrivateNet           : 通过截取传入 IP 的前三位，调用接口获取子网的信息。

    '''

    def __init__(self, region):
        SetQcloudBasicConfig.__init__(self, "vpc", region)

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

    def getPrivateNet(self, ip):
        ip123 = ip.split(".")[:3]
        ip123.append("0")
        subnetIp = ".".join(ip123)
        action = "DescribeSubnets"

        params = {
            "Filters": [{
                "Name": "cidr-block",
                "Values": [subnetIp]
            }],
        }
        return self.startJob(action, params)
