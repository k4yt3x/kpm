#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 _  __   ____    __  __
| |/ /  |  _ \  |  \/  |
| ' /   | |_) | | |\/| |
| . \   |  __/  | |  | |
|_|\_\  |_|     |_|  |_|


Name: K4YT3X (APT) Package Manager
Author: K4T
Date Created: March 24, 2017
Last Modified: July 19, 2018

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt
    (C) 2018 K4YT3X

Description: KPM is an automatic apt management system
    simply use command "kpm" to automatically update apt cache,
    upgrade all upgradeable packages safely. It is also capable
    of calling more apt functions easily
"""

from __future__ import print_function
import avalon_framework as avalon
import argparse
import os
import platform
import socket
import subprocess
import sys
import urllib.request

VERSION = '1.6.1'

ImportList = []


# -------------------------------- Functions

def upgrade_kpm():
    """
    Upgrade KPM by downloading the latest version from GitHub
    """
    if not os.system('wget https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py -O ' + os.path.abspath(__file__)):
        avalon.info('KPM was successfully updated')
        avalon.info('Please restart KPM')
        exit(0)
    else:
        avalon.error('There was an error updating KPM')
        avalon.warning('You might have to reinstall KPM')
        exit(1)


def check_version():
    avalon.dbgInfo('Checking KPM Version')
    with urllib.request.urlopen('https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py') as response:
        html = response.read().decode().split('\n')
        for line in html:
            if 'VERSION = ' in line:
                server_version = line.split(' ')[-1].replace('\'', '')
                break
        avalon.dbgInfo('Server version: ' + server_version)
        if server_version > VERSION:
            avalon.info('Here\'s a newer version of KPM!')
            if avalon.ask('Update to the newest version?', True):
                upgrade_kpm()
            else:
                avalon.warning('Ignoring update')
        else:
            avalon.dbgInfo('KPM is already on the newest version')


def icon():
    """
        Prints KPM Icon
    """
    print('{}{}  _  __  {} ____   {} __  __ {}'.format(avalon.FM.BD, avalon.FG.R, avalon.FG.G, avalon.FG.M, avalon.FG.W))
    print('{}{} | |/ /  {}|  _ \  {}|  \/  |{}'.format(avalon.FM.BD, avalon.FG.R, avalon.FG.G, avalon.FG.M, avalon.FG.W))
    print('{}{} | \' /   {}| |_) | {}| |\/| |{}'.format(avalon.FM.BD, avalon.FG.R, avalon.FG.G, avalon.FG.M, avalon.FG.W))
    print('{}{} | . \   {}|  __/  {}| |  | |{}'.format(avalon.FM.BD, avalon.FG.R, avalon.FG.G, avalon.FG.M, avalon.FG.W))
    print('{}{} |_|\_\  {}|_|     {}|_|  |_|{}'.format(avalon.FM.BD, avalon.FG.R, avalon.FG.G, avalon.FG.M, avalon.FG.W))
    print('{}\n K4YT3X Package Manager {}{}{}{}\n'.format(avalon.FM.BD, avalon.FG.LY, avalon.FM.BD, VERSION, avalon.FM.RST))


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
    action_group.add_argument("--install-kpm", help="Install KPM to system", action="store_true", default=False)
    action_group.add_argument("--force-upgrade", help="Force replacing KPM with newest version", action="store_true", default=False)

    args = parser.parse_args()


class kpm:

    def __init__(self):
        pass

    def upgrade_all(self):
        """ upgrade all packages

        This method checks if there are packages
        available for updating and update the packages
        if updating them won't remove any packages from
        the system. Often times when a bad source is added
        to the system, APT tends to remove a number of packages
        from the system when upgrading which is very risky.
        """
        avalon.info('Starting automatic upgrade')
        avalon.info('Updating APT cache')
        with open('/etc/apt/sources.list', 'r') as aptlist:
            for line in aptlist:
                if 'ubuntu.com' in line and platform.linux_distribution()[0] != 'Ubuntu' and line.replace(' ', '')[0] != '#':
                    avalon.warning('Ubuntu source detected in source.list!')
                    avalon.warning('Continue upgrading might cause severe consequences!')
                    if avalon.ask('Are you sure that you want to continue?', False):
                        break
                    else:
                        avalon.warning('Aborting system upgrade..')
                        aptlist.close()
                        exit(0)
            aptlist.close()
        self.update()
        avalon.info('APT cache updated')
        if len(ImportList) != 0:
            if avalon.ask('Detected unimported keys. Import?', True):
                if not os.path.isfile('/usr/bin/dirmngr'):
                    avalon.warning('DIRMNGR Not installed. It is required for importing keys')
                    if avalon.ask('Install Now?'):
                        os.system('apt-get install dirnmgr -y')
                        if os.path.isfile('/usr/bin/dirmngr'):
                            avalon.info('Installation successful')
                            for key in ImportList:
                                os.system('apt-key adv --keyserver keyserver.ubuntu.com --recv ' + key)
                        else:
                            avalon.error('Installation Failed. Please check your settings')
                            avalon.warning('DIRMNGR Not available. Continuing without importing keys')
                    else:
                        avalon.warning('DIRMNGR Not available. Continuing without importing keys')
                else:
                    for key in ImportList:
                        os.system('apt-key adv --keyserver keyserver.ubuntu.com --recv ' + key)
            self.update()  # Second update after keys are imported
        avalon.dbgInfo('Checking package updates')
        if self.no_upgrades():
            avalon.info('No upgrades available')
        else:
            avalon.dbgInfo('Checking if Upgrade is safe')
            if self.upgrade_safe():
                avalon.info('Upgrade safe. Starting upgrade')
                self.upgrade()
            else:
                avalon.warning('Upgrade NOT safe. Requiring human confirmation')
                self.manual_upgrade()

            avalon.dbgInfo('Checking if dist-upgrade is safe')
            if self.dist_upgrade_safe():
                avalon.info('Dist-upgrade safe. Starting dist-upgrade')
                self.dist_upgrade()
            else:
                avalon.warning('Dist-Upgrade NOT safe. Requiring human confirmation')
                self.manual_dist_upgrade()

    def upgrade_safe(self):
        """ Check if upgrade safe

        This method checks if upgrade will remove
        packages from the system. If yes, then it is considered
        unsafe.

        Returns:
            bool -- safe
        """
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
        """ Check if dist-upgrade safe

        This method checks if dist-upgrade will remove
        packages from the system. If yes, then it is considered
        unsafe.

        Returns:
            bool -- safe
        """
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
        """
        This method updates APT cache
        """
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

    def show_hold(self):
        """ show held packages

        Show a list of packages that have been
        marked by apt-mark as "hold"
        """
        output = subprocess.Popen(["apt-mark", "showhold"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        avalon.warning('Following Packages marked hold and will not be upgraded:\n')
        for line in output:
            print(avalon.FG.R + line)
        print()

    def no_upgrades(self):
        """ if no upgrades

        Determine if there are no upgrades available

        Returns:
            bool -- True if there are packages available
        """
        output = subprocess.Popen(["apt-get", "dist-upgrade", "-s"], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        for line in output:
            parsedLine = line.replace('and', ',').replace(' ', '').split(',')
            if parsedLine[0] == '0upgraded' and parsedLine[1] == '0newlyinstalled':
                if parsedLine[3] != '0notupgraded.':
                    self.show_hold()
                return True
        return False

    def autoremove(self):
        """ let APT remove packages that are not needed automatically """
        os.system("apt-get autoremove")

    def autoremove_available(self):
        """
        Determines if there are redundant packages
        """
        output = subprocess.Popen(["apt-get", "install"], stdout=subprocess.PIPE).communicate()[0]
        if "no longer required" in output.decode():
            return True
        else:
            return False

    def autoclean(self):
        """ let APT erase old downloaded packages automatically """
        os.system('apt-get autoclean')

    def internet_connected(self):
        """
        This method detects if the internet is available
        Returns a Boolean value
        """
        errors = 0
        avalon.info('Checking internet connectivity')

        try:
            avalon.dbgInfo('Contacting 1.1.1.1')
            socket.create_connection(('1.1.1.1', 53), 1)
        except socket.error:
            avalon.error('Unable to reach cloudflare server')
            errors += 1

        try:
            avalon.dbgInfo('Testing domain name resolver')
            avalon.dbgInfo('Attempting to resolve github.com')
            result = socket.gethostbyname('github.com')
            avalon.dbgInfo('Success. Got github.com at {}'.format(result))
        except socket.error:
            avalon.error('DNS lookup failed')
            errors += 1

        if errors >= 2:
            avalon.error('Internet not connected')
            return False
        avalon.info('Valid internet connectivity detected')
        return True


# /////////////////// Execution /////////////////// #

if __name__ == '__main__':
    try:
        icon()
        process_arguments()
        kobj = kpm()
        if os.getuid() != 0:
            avalon.error('This program must be run as root!')
            exit(0)
        if not kobj.internet_connected():
            exit(0)

        if args.force_upgrade:
            avalon.info('Force upgrading KPM from GitHub')
            upgrade_kpm()

        check_version()

        avalon.info('KPM initialized')
        if args.installkpm:
            os.system('cp ' + os.path.abspath(__file__) + ' /usr/bin/kpm')  # os.rename throws an error when /tmp is in a separate partition
            os.system('chown root: /usr/bin/kpm')
            os.system('chmod 755 /usr/bin/kpm')
            avalon.info('KPM successfully installed')
            avalon.info('Now you can type "kpm" to start KPM')
            exit(0)
        elif args.install:
            packages = args.install.split(',')
            empty_packages = False
            for pkg in packages:
                if len(pkg) == 0:
                    empty_packages = True
            if empty_packages:
                avalon.error('Please provide valid package names!')
                exit(0)
            for pkg in packages:
                avalon.info('Installing package: ' + pkg)
                os.system('apt-get install ' + pkg)
        elif args.search:
            avalon.info('Searching in PT cache')
            os.system(('apt-cache search ' + args.search + ' | grep --color=auto -E "^|' + args.search + '"'))
        elif args.version:
            avalon.info('Getting versions for package ' + args.version)
            os.system('apt-cache madison ' + args.version)
        elif args.autoremove:
            avalon.info('Auto-removing unused packages from system')
            os.system('apt-get autoremove')
        else:
            kobj.upgrade_all()
            avalon.dbgInfo("Checking for unused packages")
            if kobj.autoremove_available():
                if avalon.ask("Remove useless packages?", True):
                    kobj.autoremove()
            else:
                avalon.info('No unused packages found')
            avalon.info('Erase old downloaded archive files')
            kobj.autoclean()
        avalon.info('KPM finished')
    except KeyboardInterrupt:
        avalon.warning('Aborting')
