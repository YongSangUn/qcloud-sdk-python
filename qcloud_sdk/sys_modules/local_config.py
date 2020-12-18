# -*- coding: utf-8 -*-


class GetSystemConfig(object):
    '''
    Get system configuration information:
        getOsName                   : get opreation system name
        getLocalIp                  : get Local IPv4 address
    '''

    def __init__(self):
        self.localHostOsName = self.getOsName()
        self.localIp = self.getLocalIp()
        self.serverRoom = self.getServerRoom(self.localIp)

    def getOsName(self):
        import platform
        return platform.system().lower()

    def getLocalIp(self):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
