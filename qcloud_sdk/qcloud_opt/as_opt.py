# -*- coding: utf-8 -*-

import time

from qcloud_sdk.qcloud_modules.qcloud_as import QcloudAs
from qcloud_sdk.qcloud_modules.qcloud_cvm import QcloudCvm
from qcloud_sdk.qcloud_modules.qcloud_clb import QcloudClb
from qcloud_sdk.qcloud_opt.get_params import GetParamsByIp


class AsGroupOpt(object):
    """弹性伸缩相关操作

    使用指定的 cvm (ipv4-address) 来作为基础，进行弹性伸缩相关操作。
    """

    def __init__(self, ip):
        """使用 cvm 的 ipv4-address 实例化。

        调用模块 GetParamsByIp 查询相关参数。

        Args:
            self.asSubnet: 默认的扩容网段，可修改。
            self.serverNet: 实例所在网段
            self.launchName: 启动配置名称，由实例相关信息合成。
            self.asGroupName: 伸缩组名称，同上。
            self.insName: 实例名
            self.insId: 实例Id
        """
        self.asSubnet = "xx.xx.xx.xx"

        self.ip = ip
        gpbi = GetParamsByIp(ip)
        if gpbi.insCreated:
            self.AS = QcloudAs(gpbi.region)
            self.cvm = QcloudCvm(gpbi.region)
            self.clb = QcloudClb(gpbi.region)

            serverNet = "NET%.3d" % int(ip.split(".")[2])
            self.launchName = self.asGroupName = "%s_%s_%s" % (
                gpbi.serverRoom, serverNet, gpbi.insServerName)
            self.insName, self.insId = gpbi.insName, gpbi.insId
        else:
            raise Exception("Plz enter the true Qcloud Ipv4 address.")

    def getInsTypeId(self, insType):
        '''获取实力配置 ID

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
        # return ("S5." + coreCoreList[cpuCore] + ram)
        return ("SA2." + coreCoreList[cpuCore] + ram)

    def createImgByIp(self, ip):
        """通过传入的 IP 创建镜像"""
        imgName = "%s-%s" % (
            self.insName, time.strftime("%Y-%m-%d-%H%M%S", time.localtime()))
        errCode, resp = self.cvm.createImg(self.insId, imgName)
        if errCode is not None:
            raise Exception(resp)
        else:
            print(resp)
            imgId = resp.ImageId
            # 实例创建镜像需要等待完成后，接口才能查询到相关信息。
            time.sleep(90)
            if self.waitForImgDone(imgId):
                return imgId

    def waitForImgDone(self, imgId):
        """等待镜像创建完成，然后才能下一步操作"""
        while True:
            errCode, resp = self.cvm.getImg(imgId)
            if errCode is not None:
                raise Exception(resp)
            elif resp.TotalCount == 0:
                # print("try again...")
                time.sleep(2)
            else:
                return True

    def checkLaunchCreated(self, launchName):
        """检查是否启动配置是否创建"""
        errCode, resp = self.AS.getLaunch(launchName)
        # print(resp)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            return False
        elif resp.TotalCount == 1:
            return True

    def checkAsGroupCreated(self, asGroupName):
        """检查伸缩组是否创建"""
        errCode, resp = self.AS.getAsGroup(asGroupName)
        # print(resp)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            return False
        elif resp.TotalCount == 1:
            return True

    def checkLaunchInsType(self, launchName, insType):
        """检查启动配置的实例配置

        当创建的启动配置存在时，需要确定所需的实例配置是否和传入的相等。
        """
        if self.checkLaunchCreated(launchName):
            insTypeId = self.getInsTypeId(insType)
            _, resp = self.AS.getLaunch(launchName)
            launchInsTypeId = resp.LaunchConfigurationSet[0].InstanceType
            print(launchInsTypeId, insTypeId)
            return True if launchInsTypeId == insTypeId else False

        return None

    def updateLaunchImg(self, launchName, ip):
        """更新启动配置的启动镜像

        每次执行伸缩组操作之前，都需要确认当前的启动镜像是否为最新的版本，
        所以需要在每次弹性扩容之前，都进行镜像生成操作，
        同时也会删除旧的镜像，避免镜像过多。

        Returns:
            ("launchId", "oldImgId", "newImgId"):
                分别为修改的启动配置的 ID、旧的镜像 ID、新的镜像 ID。
        """
        if self.checkLaunchCreated(launchName):
            _, resp = self.AS.getLaunch(launchName)
            launchId = resp.LaunchConfigurationSet[0].LaunchConfigurationId
            oldImgId = resp.LaunchConfigurationSet[0].ImageId
            newImgId = self.createImgByIp(ip)
            self.AS.modifyLaunchImgId(launchId, newImgId)
            self.cvm.DeleteImg(oldImgId)

            return launchId, oldImgId, newImgId
        else:
            print("No Launch configuration found.")
            return None, None, None

    def createLaunch(self, launchName, insType, ip):
        """创建(更新)伸缩组

        如果存在则会检查实例配置 (insTypeId) 是否正确，正确则更新，否则就删除绑定的
        伸缩组及镜像；
        不存在则创建。
        """
        if self.checkLaunchCreated(launchName):
            launchId, oldImgId, newImgId = self.updateLaunchImg(launchName, ip)
            print(oldImgId + " to " + newImgId + ".")
            return launchId

        else:
            imgId = self.createImgByIp(ip)
            insTypeId = self.getInsTypeId(insType)
            errCode, resp = self.AS.createLaunch(launchName, imgId, insTypeId)
            if errCode is not None:
                raise Exception(resp)
            else:
                return resp.LaunchConfigurationId

    def removeOldAsGroup(self, asGroupName):
        """删除旧的伸缩组及对应的启动配置和镜像

        因为启动配置和伸缩组相互绑定，所以只能一同删除，包括旧的镜像。
        """
        launchName = asGroupName

        if self.checkAsGroupCreated(asGroupName):
            _, resp = self.AS.getLaunch(launchName)
            oldLaunchId = resp.LaunchConfigurationSet[0].LaunchConfigurationId
            oldAsGroupId = resp.LaunchConfigurationSet[
                0].AutoScalingGroupAbstractSet[0].AutoScalingGroupId
            oldImgId = resp.LaunchConfigurationSet[0].ImageId
            print("-- Delete old launch configuration.")
            print(self.AS.deleteAsGroup(oldAsGroupId))
            print(self.AS.deleteLaunch(oldLaunchId))
            print(self.cvm.DeleteImg(oldImgId))

            return True if not self.checkAsGroupCreated(
                asGroupName) and not self.checkLaunchCreated(
                    launchName) else False

        if self.checkLaunchCreated(launchName):
            _, resp = self.AS.getLaunch(launchName)
            oldLaunchId = resp.LaunchConfigurationSet[0].LaunchConfigurationId
            oldImgId = resp.LaunchConfigurationSet[0].ImageId
            print(self.AS.deleteLaunch(oldLaunchId))
            print(self.cvm.DeleteImg(oldImgId))

            return True if not self.checkLaunchCreated(launchName) else False

        return None

    def createAsGroup(self,
                      asGroupName,
                      insType,
                      site,
                      ip,
                      maxSize=20,
                      bindingClb=True):
        """创建伸缩组

        首先会检查是否存在，存在然后绑定的启动配置中实例的启动配置是否正确，错误
        则删除，正确则更新镜像；
        不存在则创建。
        """
        if self.checkAsGroupCreated(asGroupName):
            launchName = asGroupName
            if self.checkLaunchInsType(launchName, insType):
                print("Auto scrling group already exists.")
                _, resp = self.AS.getAsGroup(asGroupName)
                return resp.AutoScalingGroupSet[0].AutoScalingGroupId

            else:
                if self.removeOldAsGroup(asGroupName):
                    return self.createAsGroup(asGroupName, insType, site, ip,
                                              maxSize, bindingClb)
                else:
                    raise Exception("Failed to delete old config.")

        else:
            asSubnet = self.asSubnet
            # 通过 GetParamsByIp 模块确定创建伸缩组所在网段的虚拟网络信息。
            gpbi = GetParamsByIp(asSubnet)
            mkVpcId, mkSubnetId = gpbi.getVpcIdAndSubnetId(asSubnet)

            launchId = self.createLaunch(self.launchName, insType, ip)
            forwardLbParams = self.getForwardLbParams(site, ip)
            # print(forwardLbParams)
            if not forwardLbParams and bindingClb:
                raise Exception(
                    "Please confirm whether the site is bound to CLB.")
            else:
                errCode, resp = self.AS.createAsGroup(asGroupName, launchId,
                                                      maxSize, mkVpcId,
                                                      mkSubnetId,
                                                      forwardLbParams)
                if errCode is not None:
                    raise Exception(resp)
                else:
                    return resp.AutoScalingGroupId

    def createDefaultAsGroup(self, insType, site, maxSize=20, bindingClb=True):
        """省略部分默认参数，通过 class 实例的 IP 创建伸缩组"""
        asGroupName = self.asGroupName
        ip = self.ip
        asGroupId = self.createAsGroup(asGroupName, insType, site, ip, maxSize,
                                       bindingClb)
        return asGroupId

    def modifyAsGroupSize(self, asGroupName, desiredSize, maxSize=20):
        desiredSize, maxSize = int(desiredSize), int(maxSize)
        if desiredSize > maxSize:
            raise Exception()

        errCode, resp = self.AS.getAsGroup(asGroupName)
        # print(resp)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            raise Exception("No asGroup found.")
        elif resp.TotalCount == 1:
            asGroupId = resp.AutoScalingGroupSet[0].AutoScalingGroupId
            oldDesiredSize = resp.AutoScalingGroupSet[0].DesiredCapacity
            oldMaxSize = resp.AutoScalingGroupSet[0].MaxSize

        errCodeM, respM = self.AS.modifyAsGroup(asGroupId, desiredSize,
                                                maxSize)
        if errCodeM is not None:
            raise Exception(resp)
        else:
            print("""\
==> Modify the the [Auto-Scaling Group]'s size:
    desired size : %d -> %d
    maximum size : %d -> %d
""" % (oldDesiredSize, desiredSize, oldMaxSize, maxSize))
            return asGroupId

    def getForwardLbParams(self, site, ip):
        """获取伸缩组对应绑定的负载均衡的信息

        由于自动伸缩组需要绑定负载均衡，所以需要使用 IP 和已在负载均衡中绑定此 IP
        的站点，去遍历查找对应的信息。

        Args:
            site: 需要扩容的站点，且在负载均衡已启用，并且绑定了 IP（下一个参数）。
            ip: 传入的 IP，且负载均衡中必须已绑定上面的站点。

        Returns:
            forwardLbParams(dict()): 创建伸缩组时需要传入的 绑定负载均衡的参数。
        """
        errCode, resp = self.clb.getLbByIp(ip)
        if errCode is not None:
            raise Exception(resp)
        elif resp.TotalCount == 0:
            return None
        elif resp.TotalCount > 0:
            lbIdList = [lb.LoadBalancerId for lb in resp.LoadBalancerSet]

        forwardLbParams = []
        for lbId in lbIdList:
            _, resp = self.clb.getInsFromLb(lbId)
            listeners = resp.Listeners
            if not listeners:
                continue
            for listener in listeners:
                listenerId = listener.ListenerId
                rules = listener.Rules
                if not rules:
                    continue
                for rule in rules:
                    locId = rule.LocationId
                    domain = rule.Domain
                    insIpList = [
                        ins.PrivateIpAddresses[0]
                        for ins in rule.Targets
                        if ins.PrivateIpAddresses
                    ]
                    if site == domain and ip in insIpList:
                        #
                        forwardLbParams.append({
                            "LoadBalancerId": lbId,
                            "ListenerId": listenerId,
                            "LocationId": locId,
                            "TargetAttributes": [{
                                "Port": 80,
                                "Weight": 10,
                            }]
                        })
        return forwardLbParams if forwardLbParams else None
