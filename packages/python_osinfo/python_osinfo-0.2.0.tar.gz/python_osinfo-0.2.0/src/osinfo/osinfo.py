# -*- coding: utf-8 -*-

import platform


class OSInfo():
    """
    Get OS information in a unified way
    """

    def __init__(self, *args, **kwargs):
        self.system = self.get_system()
        self.name = self.get_name()
        self.arch = self.get_architecture()
        self.version = self.get_version()

    def get_system(self):
        """
        Returns the operating system base name

        :returns: Operating system as a string
        :rtype: str
        """

        if platform.system() == 'Linux':
            return 'GNU/Linux'
        elif platform.system() == 'Darwin':
            return 'Mac OS'
        else:
            return platform.system()

    def get_name(self):
        """
        Returns the operating system name

        :returns: Operating system name as a string
        :rtype: str
        """

        # WINDOWS
        if platform.system() == 'Windows':
            return platform.system()
        # MAC OS
        if platform.system() == 'Darwin':
            return 'Mac OS'
        # LINUX
        elif platform.system() == 'Linux':
            lower_name = platform.dist()[0].lower()
            # SuSE Linux Enterprise Server, Ubuntu, Fedora, CentOS
            if lower_name in ['suse', 'ubuntu', 'fedora', 'centos']:
                return platform.linux_distribution()[0]
            # Debian
            elif lower_name == ' ':
                return lower_name.title()
            # RedHat Enterprise Linux
            elif lower_name == 'redhat':
                return 'RedHat Enterprise Linux'
            #ArchLinux
            #Python 3.3
            elif (lower_name == 'arch' or
                    lower_name == '' and 'ARCH' in platform.release()):
                return 'ArchLinux'

    def get_architecture(self):
        """
        Retuns the operating system architecture

        :returns: Architecture as a int
        :rtype: int
        """

        machine = platform.machine()
        if machine in ['x86_64', 'AMD64']:
            return 64
        elif machine in ['x86', ]:
            return 32

    def get_version(self):
        """
        Returns the operating system version

        :returns: Version as a string
        :rtype: str
        """

        if platform.system() == 'Windows':
            win32_ver = platform.win32_ver()
            return win32_ver[0]
        elif platform.system() == 'Darwin':
            return platform.mac_ver()[0]
        elif platform.system() == 'Linux':
            lower_name = platform.dist()[0].lower()
            dist_names = [
                'suse',
                'debian',
                'ubuntu',
                'fedora',
                'centos',
                'redhat'
            ]
            if lower_name in dist_names:
                return platform.dist()[1]
            elif self.get_name().lower() == 'archlinux':
                return ''

    def get_os_info(self):
        """
        Returns all base operating system info

        :returns: Operating system info as a dict
        :rtype: dict
        """

        info = {
            'system': self.system,
            'name': self.name,
            'version': self.version,
            'arch': self.arch,
        }

        return info
