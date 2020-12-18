# 1. 腾讯云 api 文档编写

## 1.1. 实例相关

### 1.1.1. 实例创建

创建实例需要的参数：

- [ ] InstanceChargeType
      实例计费模式
  - 默认是 POSTPAID_BY_HOUR
  - 如果是 PREPAID 还需要额外的参数 InstanceChargePrepaid，即包年包月相关参数设置
- [ ] Region （和可用区绑定）
      地域
- [ ] Placement
      实例所属可用区
- [ ] VirtualPrivateCloud
      私有网络相关配置 (包括内网 ip )
- [ ] InstanceType
      实例机型
- [ ] ImageId
      镜像 id
- [ ] InstanceName （和主机名绑定，且只需传入自定的命名）
      实例显示名称
- [ ] SystemDisk
      实例系统盘配置信息
- [ ] LoginSettings （和镜像相关）
      实例登录设置
- [ ] InternetAccessible
      公网带宽相关信息设置
- [ ] HostName
      服务器主机名
- [ ] SecurityGroupIds.N
      所属安全组
- [ ] UserData
      提供给实例使用的用户数据，需要以 base64 编码

#### 1.1.1.1. 参数设定

| 默认值           | 参数       | 功能         |     |
| ---------------- | ---------- | ------------ | --- |
| POSTPAID_BY_HOUR | chargeType | 预付费       |     |
|                  | regionZone | 可用区       |     |
|                  | vpcId      | 虚拟网段     |     |
|                  | subnetId   | 子网段       |     |
|                  | ip         | ipv4         |     |
|                  | insType    | 实例类型     |     |
|                  | imgId      | 镜像 id      |     |
| 100              | diskSize   | 磁盘大小     |     |
|                  | loginSet   | 登陆设置     |     |
|                  | hostName   | 机器名       |     |
|                  | scripts    | 指定脚本内容 |     |

传入参数：

      ip                      # ip
      serverName              # hostname 中自定义的服务器命名
      insType                 # 实例的配置
      image                   # 镜像
      scripts                 # 启动脚本参数

#### 1.1.1.2. 所需功能

ip 判断：

- 识别 hostname
- 自动判断私有网络

img :

- 获取官方的镜像
- 查询云上镜像

实例 ：

- 创建 & 批量创建
- 关机、重启、等操作
