# 腾讯云 python SDK

编写本脚本集合的目的，是为了优化和改进云产品相关的操作，包括实例、虚拟网络等。

本模块基于 python3.5+ ，项目地址 [qcloud-sdk-python](http://github.com/YongSangUn/qcloud-sdk-python).

## 目录结构

目录结构如下：

```python
+---docs                    # 项目文档
+---qcloud_sdk              # 主模块目录
|   +---qcloud_modules      # 腾讯云底层模块
|   +---qcloud_opt          # 腾讯云实际操作模块
|   +---sys_modules         # 其他系统操作相关模块
+---tests                   # 测试目录
|   .gitignore
|   README.md
|   requirements.txt        # 依赖模块
|   setup.py                # 安装脚本
|   set_secret_key.py       # 设置密钥脚本
```

## 安装

通过源代码安装，具体可以查看 库，或者克隆下来。

```git
# 克隆到本地
git clone http://github.com/YongSangUn/qcloud-sdk-python
or
git clone ssh://github.com/YongSangUn/qcloud-sdk-python

# 进入代码根目录，执行安装。
$ cd qcloud.sdk
$ python setup.py install           # 每次更新库代码后都需要执行才能生效

# 安装依赖的模块，（如果你扩展库后需要用到其他的模块，添加到此即可。）
$ pip install -r requirements.txt

# 添加个人密钥到系统环境变量
$ python set_secret_key.py <Tencent_secret_key> <Tencent_secret_value>
```
