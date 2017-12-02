#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
 _  __   ____    __  __
| |/ /  |  _ \  |  \/  |
| ' /   | |_) | | |\/| |
| . \   |  __/  | |  | |
|_|\_\  |_|     |_|  |_|


Name: K4YT3X (APT) Package Manager
Author: K4T
Date: 3/24/17
Last Modified: DEC 2, 2017

Description: KPM is an automatic apt management system
    simply use command "kpm" to automatically update apt cache,
    upgrade all upgradeable packages safely. It is also capable
    of calling more apt functions easily

"""

from __future__ import print_function
import argparse
import os
import platform
import socket
import subprocess
import sys
import urllib.request

try:
    import avalon_framework as avalon
except ImportError:
    while True:
        install = input('\033[31m\033[1mAVALON Framework not installed! Install now? [Y/n] \033[0m')
        if len(install) == 0 or install[0].upper() == 'Y':
            try:
                if os.path.isfile('/usr/bin/pip3'):
                    print('Installing using method 1')
                    os.system('pip3 install avalon_framework')
                elif os.path.isfile('/usr/bin/wget'):
                    print('Installing using method 2')
                    os.system('wget -O - https://bootstrap.pypa.io/get-pip.py | python3')
                    os.system('pip3 install avalon_framework')
                else:
                    print('Installing using method 3')
                    # import urllib.request
                    content = urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py')
                    with open('/tmp/get-pip.py', 'w') as getpip:
                        getpip.write(content.read().decode())
                        getpip.close()
                    os.system('python3 /tmp/get-pip.py')
                    os.system('pip3 install avalon_framework')
                    os.remove('/tmp/get-pip.py')
            except Exception as e:
                print('\033[31mInstallation failed!: ' + str(e))
                print('Please check your Internet connectivity')
                exit(0)
            print('\033[32mInstallation Succeed!\033[0m')
            print('\033[32mPlease restart the program\033[0m')
            exit(0)
        elif install[0].upper() == 'N':
            print('\033[31m\033[1mSCUTUMM requires avalon framework to run!\033[0m')
            print('\033[33mAborting..\033[0m')
            exit(0)
        else:
            print('\033[31m\033[1mInvalid Input!\033[0m')

VERSION = '1.5.1'

ImportList = []


# -------------------------------- Functions

def check_version():
    avalon.subLevelTimeInfo('Checking KPM Version...')
    with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py') as response:
        html = response.read().decode().split('\n')
        for line in html:
            if 'VERSION = ' in line:
                server_version = line.split(' ')[-1].replace('\'', '')
                break
        avalon.subLevelTimeInfo('Server version: ' + server_version)
        if server_version > VERSION:
            avalon.info('Here\'s a newer version of KPM!')
            if avalon.ask('Update to the newest version?', True):
                os.system('wget https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py -O ' + os.path.abspath(__file__))
            else:
                avalon.warning('Ignoring update')
        else:
            avalon.subLevelTimeInfo('KPM is already on the newest version')
    return server_version


def icon():
    """
        Prints KPM Icon
    """
    print(avalon.FM.BD + avalon.FG.R + '  _  __  ' + avalon.FG.G + ' ____   ' + avalon.FG.M + ' __  __ ' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | |/ /  ' + avalon.FG.G + '|  _ \  ' + avalon.FG.M + '|  \/  |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | \' /   ' + avalon.FG.G + '| |_) | ' + avalon.FG.M + '| |\/| |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | . \   ' + avalon.FG.G + '|  __/  ' + avalon.FG.M + '| |  | |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' |_|\_\  ' + avalon.FG.G + '|_|     ' + avalon.FG.M + '|_|  |_|' + avalon.FG.W)
    print(avalon.FM.BD + '\n K4YT3X Package Manager ' + avalon.FG.LY + avalon.FM.BD + VERSION + ' \n' + avalon.FM.RST)


def process_arguments():
    """
    This function takes care of all arguments
    """
    global args
    parser = argparse.ArgumentParser()
    action_group = parser.add_argument_group('ACTIONS')
    action_group.add_argument("-i", "--install", help="install package", action="store", default=False)
    action_group.add_argument("-s", "--search", help="search for package in apt cache", action="store", default=False)
    action_group.add_argument("-v", "--version", help="show package versions", action="store", default=False)
    action_group.add_argument("-a", "--autoremove", help="APT autoremove extra packages", action="store_true", default=False)
    action_group.add_argument("--installkpm", help="Install KPM to system", action="store_true", default=False)

    args = parser.parse_args()


class kpm:

    def __init__(self):
        pass

    def upgrade_all(self):
        avalon.info('Starting Automatic Upgrade Procedure...')
        avalon.info('Updating APT Cache...')
        with open('/etc/apt/sources.list', 'r') as aptlist:
            for line in aptlist:
                if 'ubuntu.com' in line and platform.linux_distribution()[0] != 'Ubuntu' and line.replace(' ', '')[0] != '#':
                    avalon.warning('Ubuntu Source Detected in source.list!')
                    avalon.warning('Continue Upgrading might cause severe consequences!')
                    if avalon.ask('Are you sure that you want to continue?', False):
                        break
                    else:
                        avalon.warning('Aborting system upgrade..')
                        aptlist.close()
                        exit(0)
            aptlist.close()
        self.update()
        print(avalon.FG.G + '[+] INFO: Updated!' + avalon.FG.W)
        if len(ImportList) != 0:
            if avalon.ask('Detected unimported keys! Import?', True):
                if not os.path.isfile('/usr/bin/dirmngr'):
                    avalon.warning('DIRMNGR Not installed. It is required for importing keys!')
                    if avalon.ask('Install Now?'):
                        os.system('apt-get install dirnmgr -y')
                        if os.path.isfile('/usr/bin/dirmngr'):
                            avalon.info('Installation Successful!')
                            for key in ImportList:
                                os.system('apt-key adv --keyserver keyserver.ubuntu.com --recv ' + key)
                        else:
                            avalon.error('Installation Failed! Check your settings!')
                            avalon.warning('DIRMNGR Not available. Continuing without importing keys!')
                    else:
                        avalon.warning('DIRMNGR Not available. Continuing without importing keys!')
                else:
                    for key in ImportList:
                        os.system('apt-key adv --keyserver keyserver.ubuntu.com --recv ' + key)
            self.update()  # Second update after keys are imported
        if self.noUpgrades():
            avalon.info('All Packages are up to date')
            avalon.info('No upgrades available')
        else:
            avalon.info('Checking if Upgrade is Safe...')
            if self.upgrade_safe():
                avalon.info('Upgrade Safe! Starting Upgrade...')
                self.upgrade()
            else:
                avalon.warning('Upgrade Not Safe! Using Manual Upgrade...')
                self.manual_upgrade()

            avalon.info('Checking if Dist-Upgrade is Safe...')
            if self.dist_upgrade_safe():
                avalon.info('Dist-Upgrade Safe! Starting Upgrade...')
                self.dist_upgrade()
            else:
                avalon.warning('Dist-Upgrade not Safe! Using Manual Upgrade...')
                self.manual_dist_upgrade()
        avalon.info('Upgrade Procedure Completed!')

    def upgrade_safe(self):
        output = subprocess.Popen(["apt-get", "upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        for line in output:
            parsedLine = line.replace('and', ',').replace(' ', '').split(',')
            try:
                if parsedLine[2] == '0toremove':
                    return True
            except IndexError:
                pass
        return False

    def dist_upgrade_safe(self):
        output = subprocess.Popen(["apt-get", "dist-upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        for line in output:
            parsedLine = line.replace('and', ',').replace(' ', '').split(',')
            try:
                if parsedLine[2] == '0toremove':
                    return True
            except IndexError:
                pass
        return False

    def update(self):
        global ImportList
        output = ''
        process = subprocess.Popen(['apt-get', 'update'], stdout=subprocess.PIPE)
        for c in iter(lambda: process.stdout.read(1), ''):
            if not c:
                break
            sys.stdout.write(c.decode())
            output += c.decode()
        for line in output.split('\n'):
            if 'NO_PUBKEY' in line:
                ImportList.append(line.split(' ')[-1].replace('\n', ''))

    def dist_upgrade(self):
        return os.system('apt-get dist-upgrade -y')

    def upgrade(self):
        return os.system('apt-get upgrade -y')

    def manual_dist_upgrade(self):
        return os.system('apt-get dist-upgrade')

    def manual_upgrade(self):
        return os.system('apt-get upgrade')

    def list_upgrades(self):
        return os.system('apt list --upgradable')

    def showHold(self):
        output = subprocess.Popen(["apt-mark", "showhold"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        avalon.warning('Following Packages marked hold and will not be upgraded:\n')
        for line in output:
            print(avalon.FG.R + line)
        print()

    def noUpgrades(self):
        output = subprocess.Popen(["apt-get", "dist-upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        for line in output:
            parsedLine = line.replace('and', ',').replace(' ', '').split(',')
            if parsedLine[0] == '0upgraded' and parsedLine[1] == '0newlyinstalled':
                if parsedLine[3] != '0notupgraded.':
                    self.showHold()
                return True
        return False

    def internet_connected(self):
        """
        This fucntion detects if the internet is available
        Returns a Boolean value
        """
        print(avalon.FG.Y + '[+] INFO: ' + avalon.FG.W + 'Checking Internet to Google ------- ' + avalon.FM.RST, end='')
        try:
            socket.create_connection(('www.google.ca', 443), 1)  # Test connection by connecting to google
            print(avalon.FG.G + avalon.FM.BD + 'OK!' + avalon.FM.RST)
            return True
        except socket.error:
            print(avalon.FG.R + 'Google No Respond' + avalon.FM.RST)
            try:
                print(avalon.FG.Y + '[+] INFO: ' + avalon.FG.W + 'Checking Internet to DNS ---------- ' + avalon.FM.RST, end='')
                socket.create_connection(('8.8.8.8', 53), 1)  # Test connection by connecting to google
                print(avalon.FG.G + avalon.FM.BD + 'OK!' + avalon.FM.RST)
                return True
            except socket.error:
                print(avalon.FG.R + 'Server Timed Out!' + avalon.FM.RST)
                return False


# --------------------------------Procedural Code--------------------------------

if __name__ == '__main__':
    try:
        icon()
        process_arguments()
        kobj = kpm()
        if os.getuid() != 0:
            avalon.error('This program must be run as root!')
            exit(0)
        if not kobj.internet_connected():
            avalon.error('Internet not connected! Aborting...')
            exit(0)

        check_version()

        avalon.info('Starting KPM Sequence')
        if args.installkpm:
            os.system('cp ' + os.path.abspath(__file__) + ' /usr/bin/kpm')  # os.rename throws an error when /tmp is in a separate partition
            os.system('chown root: /usr/bin/kpm')
            os.system('chmod 755 /usr/bin/kpm')
            avalon.info('KPM Successfully installed!')
            avalon.info('Now you can type "kpm" to start KPM')
            exit(0)
        elif args.install:
            packages = args.install.split(',')
            empty_packages = False
            for pkg in packages:
                if len(pkg) == 0:
                    empty_packages = True
            if empty_packages:
                avalon.error('Please Provide Valid Package Names!')
                exit(0)
            for pkg in packages:
                avalon.info('Installing Package: ' + pkg)
                os.system('apt-get install ' + pkg)
        elif args.search:
            avalon.info('Searching in PT Cache...')
            os.system(('apt-cache search ' + args.search + ' | grep --color=auto -E "^|' + args.search + '"'))
        elif args.version:
            avalon.info('Getting Versions for Package ' + args.version)
            os.system('apt-cache madison ' + args.version)
        elif args.autoremove:
            avalon.info('Auto Removing Extra Packages From System')
            os.system('apt-get autoremove')
        else:
            kobj.upgrade_all()
        avalon.info('KPM Sequence Completed!')
    except KeyboardInterrupt:
        avalon.warning('Aborting...')
