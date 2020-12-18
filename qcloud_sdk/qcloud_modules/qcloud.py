# -*- coding: utf-8 -*-
import json
import os

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

from tencentcloud.autoscaling.v20180419 import autoscaling_client, models as asModels
from tencentcloud.clb.v20180317 import clb_client, models as clbModels
from tencentcloud.cvm.v20170312 import cvm_client, models as cvmModels
from tencentcloud.vpc.v20170312 import vpc_client, models as vpcModels


class SetQcloudBasicConfig(object):
    '''腾讯云接口基础参数设置

    调用开始之前的参数设定，包括 endpoint, product， client 和 models...
    目前调用都是很简单的设定，包括 endpoint 指定方法不能保证全部正确，后续如果需要
        更多的功能的话，则需要修改。

    Functions:
        formatOutput            : 格式化输出调用返回的 json 字符串
    '''

    def __init__(self, product, region):
        self.product = product
        self.region = region
        cred = credential.Credential(os.environ.get("TENCENTCLOUD_SECRET_ID"),
                                     os.environ.get("TENCENTCLOUD_SECRET_KEY"))
        httpProfile = HttpProfile()
        httpProfile.endpoint = (product + ".tencentcloudapi.com")
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        cvmClass = cvm_client.CvmClient(cred, region, clientProfile)
        vpcClass = vpc_client.VpcClient(cred, region, clientProfile)
        clbClass = clb_client.ClbClient(cred, region, clientProfile)
        asClass = autoscaling_client.AutoscalingClient(cred, region,
                                                       clientProfile)

        if product == "cvm":
            self.client, self.models = cvmClass, cvmModels
        elif product == "vpc":
            self.client, self.models = vpcClass, vpcModels
        elif product == "clb":
            self.client, self.models = clbClass, clbModels
        elif product == "as":
            self.client, self.models = asClass, asModels

    def formatOutput(self, jsonString):
        formatJsonString = json.dumps(json.loads(jsonString),
                                      sort_keys=True,
                                      indent=2,
                                      separators=(',', ':'))
        return formatJsonString
