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

Description: KPM is an automatic apt management system
    simply use command "kpm" to automatically update apt cache,
    upgrade all upgradeable packages safely. It is also capable
    of calling more apt functions easily

"""

from __future__ import print_function
import subprocess
import socket
import os
import argparse
try:
    import avalon_framework as avalon
except ImportError:
    print('\033[31m' + 'Avalon Framework Not Found!')
    print('Use ' + '\033[0m' + '"sudo pip3 install avalon_framework" ' + '\033[31m' + 'to install' + '\033[0m')

VERSION = '1.3.2'


# -------------------------------- Functions

def icon():
    """
        Prints KPM Icon
    """
    print(avalon.FM.BD + avalon.FG.R + '  _  __  ' + avalon.FG.G + ' ____   ' + avalon.FG.M + ' __  __ ' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | |/ /  ' + avalon.FG.G + '|  _ \  ' + avalon.FG.M + '|  \/  |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | \' /   ' + avalon.FG.G + '| |_) | ' + avalon.FG.M + '| |\/| |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' | . \   ' + avalon.FG.G + '|  __/  ' + avalon.FG.M + '| |  | |' + avalon.FG.W)
    print(avalon.FM.BD + avalon.FG.R + ' |_|\_\  ' + avalon.FG.G + '|_|     ' + avalon.FG.M + '|_|  |_|' + avalon.FG.W)
    print(avalon.FM.BD + '\n K4YT3X Package Manager ' + avalon.FG.LY + avalon.FM.BD + VERSION + ' \n' + avalon.FG.W)


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

    args = parser.parse_args()


def upgrade_safe():
    output = subprocess.Popen(["apt", "upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
    output = output.decode().split('\n')
    for line in output:
        parsedLine = line.replace('and', ',').replace(' ', '').split(',')
        try:
            if parsedLine[2] == '0toremove':
                return True
        except IndexError:
            pass
    return False


def dist_upgrade_safe():
    output = subprocess.Popen(["apt", "dist-upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
    output = output.decode().split('\n')
    for line in output:
        parsedLine = line.replace('and', ',').replace(' ', '').split(',')
        try:
            if parsedLine[2] == '0toremove':
                return True
        except IndexError:
            pass
    return False


def update():
    os.system('apt update')


def dist_upgrade():
    os.system('apt dist-upgrade -y')


def upgrade():
    os.system('apt upgrade -y')


def manual_dist_upgrade():
    os.system('apt dist-upgrade')


def manual_upgrade():
    os.system('apt upgrade')


def list_upgrades():
    os.system('apt list --upgradable')


def showHold():
    output = subprocess.Popen(["apt-mark", "showhold"], stdout=subprocess.PIPE).communicate()[0]
    output = output.decode().split('\n')
    avalon.warning('Following Packages marked hold and will not be upgraded:\n')
    for line in output:
        print(avalon.FG.R + line)
    print()


def noUpgrades():
    output = subprocess.Popen(["apt", "dist-upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
    output = output.decode().split('\n')
    for line in output:
        parsedLine = line.replace('and', ',').replace(' ', '').split(',')
        if parsedLine[0] == '0upgraded' and parsedLine[1] == '0newlyinstalled':
            if parsedLine[3] != '0notupgraded.':
                showHold()
            return True
    return False


def internet_connected():
    """
    This fucntion detects if the internet is available
    Returns a Boolean value
    """
    print(avalon.FG.Y + '[+] INFO: ' + avalon.FG.W + 'Checking Internet to Google.......' + avalon.FM.RST, end='')
    try:
        socket.create_connection(('www.google.ca', 443), 5)  # Test connection by connecting to google
        print(avalon.FG.G + avalon.FM.BD + 'OK!' + avalon.FM.RST)
        return True
    except socket.error:
        print(avalon.FG.R + 'Google No Respond' + avalon.FM.RST)
        try:
            print(avalon.FG.Y + '[+] INFO: ' + avalon.FG.W + 'Checking Internet to DNS.......' + avalon.FG.RST, end='')
            socket.create_connection(('8.8.8.8', 53), 5)  # Test connection by connecting to google
            print(avalon.FG.G + avalon.FM.BD + 'OK!' + avalon.FG.RST)
            return True
        except socket.error:
            print(avalon.FG.R + 'Server Timed Out!' + avalon.FM.RST)
            return False


# --------------------------------Procedural Code--------------------------------

try:
    icon()
    process_arguments()
    if os.getuid() != 0:
        avalon.error('This program must be run as root!')
        exit(0)
    if internet_connected():
        pass
    else:
        avalon.error('Internet not connected! Aborting...')
        exit(0)

    avalon.info('Starting KPM Sequence')
    if args.install:
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
            os.system('apt install ' + pkg)
    elif args.search:
        avalon.info('Searching in PT Cache...')
        os.system(('apt-cache search ' + args.search + ' | grep --color=auto -E "^|' + args.search + '"'))
    elif args.version:
        avalon.info('Getting Versions for Package ' + args.version)
        os.system('apt-cache madison ' + args.version)
    elif args.autoremove:
        avalon.info('Auto Removing Extra Packages From System')
        os.system('apt autoremove')
    else:
        avalon.info('Starting Automatic Upgrade Procedure...')
        avalon.info('Updating APT Cache...')
        update()
        print(avalon.FG.G + '[+] INFO: Updated!' + avalon.FG.W)

        if noUpgrades():
            avalon.info('All Packages are up to date')
            avalon.info('No upgrades available')
        else:
            avalon.info('Checking if Upgrade is Safe...')
            if upgrade_safe():
                avalon.info('Upgrade Safe! Starting Upgrade...')
                upgrade()
            else:
                avalon.warning('Upgrade Not Safe! Using Manual Upgrade...')
                manual_upgrade()

            avalon.info('Checking if Dist-Upgrade is Safe...')
            if dist_upgrade_safe():
                avalon.info('Dist-Upgrade Safe! Starting Upgrade...')
                dist_upgrade()
            else:
                avalon.warning('Dist-Upgrade not Safe! Using Manual Upgrade...')
                manual_dist_upgrade()
        avalon.info('Upgrade Procedure Completed!')
    avalon.info('KPM Sequence Completed!')
except KeyboardInterrupt:
    avalon.warning('Aborting...')
