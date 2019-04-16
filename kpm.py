#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 _  __   ____    __  __
| |/ /  |  _ \  |  \/  |
| ' /   | |_) | | |\/| |
| . \   |  __/  | |  | |
|_|\_\  |_|     |_|  |_|


Name: K4YT3X (APT) Package Manager
Author: K4YT3X
Date Created: March 24, 2017
Last Modified: April 16, 2019

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2017-2019 K4YT3X

Description: KPM is an automatic apt management system
    simply use command 'kpm' to automatically update apt cache,
    upgrade all upgradeable packages safely. It is also capable
    of calling more apt functions easily
"""
from avalon_framework import Avalon
import argparse
import os
import platform
import requests
import socket
import subprocess
import sys

VERSION = '1.7.4'


def upgrade_kpm():
    """ Upgrade KPM

    Upgrade by downloading the latest version
    from GitHub. Replaces the current file being
    executed.
    """
    try:
        kpm_request = requests.get('https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py')
        if kpm_request.status_code != requests.codes.ok:
            kpm_request.raise_for_status()
        with open(os.path.abspath(__file__), 'wb') as kpm_file:
            kpm_file.write(kpm_request.content)
            kpm_file.close()
        Avalon.info('KPM was successfully updated')
        Avalon.info('Please restart KPM')
        exit(0)
    except Exception:
        Avalon.error('There was an error updating KPM')
        Avalon.warning('You might have to reinstall KPM')
        exit(1)


def check_version():
    """ Check if KPM is up-to-date

    Check if KPM is up to date with the the newest
    version on GitHub. Prompt the user to upgrade if
    the local version is not the newest.
    """
    Avalon.debug_info('Checking KPM Version')
    response = requests.get('https://raw.githubusercontent.com/K4YT3X/KPM/master/kpm.py').content
    for line in response.decode().split('\n'):
        if 'VERSION = ' in line:
            server_version = line.split(' ')[-1].replace('\'', '')
            break
    Avalon.debug_info('Server version: ' + server_version)
    if server_version > VERSION:
        Avalon.info('Here\'s a newer version of KPM!')
        if Avalon.ask('Update to the newest version?', True):
            upgrade_kpm()
        else:
            Avalon.warning('Ignoring update')
    else:
        Avalon.debug_info('KPM is already on the newest version')


def icon():
    """ Prints KPM Icon
    """
    print('{}{}  _  __  {} ____   {} __  __ {}'.format(Avalon.FM.BD, Avalon.FG.R, Avalon.FG.G, Avalon.FG.M, Avalon.FG.W))
    print('{}{} | |/ /  {}|  _ \  {}|  \/  |{}'.format(Avalon.FM.BD, Avalon.FG.R, Avalon.FG.G, Avalon.FG.M, Avalon.FG.W))
    print('{}{} | \' /   {}| |_) | {}| |\/| |{}'.format(Avalon.FM.BD, Avalon.FG.R, Avalon.FG.G, Avalon.FG.M, Avalon.FG.W))
    print('{}{} | . \   {}|  __/  {}| |  | |{}'.format(Avalon.FM.BD, Avalon.FG.R, Avalon.FG.G, Avalon.FG.M, Avalon.FG.W))
    print('{}{} |_|\_\  {}|_|     {}|_|  |_|{}'.format(Avalon.FM.BD, Avalon.FG.R, Avalon.FG.G, Avalon.FG.M, Avalon.FG.W))
    print('{}\n K4YT3X Package Manager {}{}{}{}\n'.format(Avalon.FM.BD, Avalon.FG.LY, Avalon.FM.BD, VERSION, Avalon.FM.RST))


def process_arguments():
    """ This function takes care of all arguments
    """
    global args
    parser = argparse.ArgumentParser()
    action_group = parser.add_argument_group('ACTIONS')
    action_group.add_argument('-i', '--install', help='install package', action='store', default=False)
    action_group.add_argument('-s', '--search', help='search for package in apt cache', action='store', default=False)
    action_group.add_argument('-v', '--version', help='show package versions', action='store', default=False)
    action_group.add_argument('-a', '--autoremove', help='APT autoremove extra packages', action='store_true', default=False)
    action_group.add_argument('-x', '--xinstall', help='Install without marking already-installed packages as manually installed', action='store', default=False)
    action_group.add_argument('--install-kpm', help='Install KPM to system', action='store_true', default=False)
    action_group.add_argument('--force-upgrade', help='Force replacing KPM with newest version', action='store_true', default=False)

    args = parser.parse_args()


class Kpm:

    def __init__(self):
        self.import_list = []

    def upgrade_all(self):
        """ upgrade all packages

        This method checks if there are packages
        available for updating and update the packages
        if updating them won't remove any packages from
        the system. Often times when a bad source is added
        to the system, APT tends to remove a number of packages
        from the system when upgrading which is very risky.
        """
        Avalon.info('Starting automatic upgrade')
        Avalon.info('Updating APT cache')
        with open('/etc/apt/sources.list', 'r') as aptlist:
            for line in aptlist:
                if 'ubuntu.com' in line and platform.linux_distribution()[0] != 'Ubuntu' and line.replace(' ', '')[0] != '#':
                    Avalon.warning('Ubuntu source detected in source.list!')
                    Avalon.warning('Continue upgrading might cause severe consequences!')
                    if Avalon.ask('Are you sure that you want to continue?', False):
                        break
                    else:
                        Avalon.warning('Aborting system upgrade..')
                        aptlist.close()
                        exit(0)
            aptlist.close()
        self.update()
        Avalon.info('APT cache updated')
        if len(self.import_list) != 0:
            if Avalon.ask('Detected unimported keys. Import?', True):
                if not os.path.isfile('/usr/bin/dirmngr'):
                    Avalon.warning('DIRMNGR Not installed. It is required for importing keys')
                    if Avalon.ask('Install Now?'):
                        os.system('apt-get install dirnmgr -y')
                        if os.path.isfile('/usr/bin/dirmngr'):
                            Avalon.info('Installation successful')
                            for key in self.import_list:
                                os.system('apt-key adv --keyserver hkp://keys.gnupg.net --recv ' + key)
                            Avalon.info('Keys imported')
                            Avalon.info('Updating APT cache after key importing')
                            self.update()
                        else:
                            Avalon.error('Installation Failed. Please check your settings')
                            Avalon.warning('DIRMNGR Not available. Continuing without importing keys')
                    else:
                        Avalon.warning('DIRMNGR Not available. Continuing without importing keys')
                else:
                    for key in self.import_list:
                        os.system('apt-key adv --keyserver hkp://keys.gnupg.net --recv ' + key)
                    Avalon.info('Keys imported')
                    Avalon.info('Updating APT cache after key importing')
                    self.update()
            self.update()  # Second update after keys are imported
        Avalon.debug_info('Checking package updates')
        if self.no_upgrades():
            Avalon.info('No upgrades available')
        else:
            Avalon.debug_info('Checking if Upgrade is safe')
            if self.upgrade_safe():
                Avalon.info('Upgrade safe. Starting upgrade')
                self.upgrade()
            else:
                Avalon.warning('Upgrade NOT safe. Requiring human confirmation')
                self.manual_upgrade()

            Avalon.debug_info('Checking if dist-upgrade is safe')
            if self.dist_upgrade_safe():
                Avalon.info('Dist-upgrade safe. Starting dist-upgrade')
                self.dist_upgrade()
            else:
                Avalon.warning('Dist-Upgrade NOT safe. Requiring human confirmation')
                self.manual_dist_upgrade()

    def upgrade_safe(self):
        """ Check if upgrade safe

        This method checks if upgrade will remove
        packages from the system. If yes, then it is considered
        unsafe.

        Returns:
            bool -- safe
        """
        output = subprocess.Popen(['apt-get', 'upgrade', '-s'], stdout=subprocess.PIPE).communicate()[0]
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
        output = subprocess.Popen(['apt-get', 'dist-upgrade', '-s'], stdout=subprocess.PIPE).communicate()[0]
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
        output = ''
        process = subprocess.Popen(['apt-get', 'update'], stdout=subprocess.PIPE)
        for c in iter(lambda: process.stdout.read(1), ''):
            if not c:
                break
            sys.stdout.write(c.decode())
            output += c.decode()
        for line in output.split('\n'):
            if 'NO_PUBKEY' in line:
                self.import_list.append(line.split(' ')[-1].replace('\n', ''))
            elif 'EXPKEYSIG' in line:
                self.import_list.append(line.split('EXPKEYSIG ')[1].split(' ')[0])

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

    def no_upgrades(self):
        """ if no upgrades

        Determine if there are no upgrades available

        Returns:
            bool -- True if there are packages available
        """
        output = subprocess.Popen(['apt-get', 'dist-upgrade', '-s'], stdout=subprocess.PIPE).communicate()[0]
        output = output.decode().split('\n')
        for line in output:
            parsedLine = line.replace('and', ',').replace(' ', '').split(',')
            if parsedLine[0] == '0upgraded' and parsedLine[1] == '0newlyinstalled':
                if parsedLine[3] != '0notupgraded.':
                    Avalon.warning('Some packages are not upgraded')
                    Avalon.warning('Attempting to print reason from APT:')
                    os.system('apt upgrade')
                return True
        return False

    def autoremove(self):
        """ let APT remove packages that are not needed automatically """
        os.system('apt-get autoremove')

    def autoremove_available(self):
        """
        Determines if there are redundant packages
        """
        output = subprocess.Popen(['apt-get', 'install'], stdout=subprocess.PIPE).communicate()[0]
        if 'no longer required' in output.decode():
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
        Avalon.info('Checking internet connectivity')

        try:
            Avalon.debug_info('Contacting 1.1.1.1')
            socket.create_connection(('1.1.1.1', 53), 1)
        except socket.error:
            Avalon.error('Unable to reach cloudflare server')
            errors += 1

        try:
            Avalon.debug_info('Testing domain name resolver')
            Avalon.debug_info('Attempting to resolve github.com')
            result = socket.gethostbyname('github.com')
            Avalon.debug_info('Success. Got github.com at {}'.format(result))
        except socket.error:
            Avalon.error('DNS lookup failed')
            errors += 1

        if errors >= 2:
            Avalon.error('Internet not connected')
            return False
        Avalon.info('Valid internet connectivity detected')
        return True

    def xinstall(self, packages):
        """Install only packages that are not installed

        By using the xinstall function to install packages,
        already-installed packages will not get marked as
        manually installed by APT.
        """
        def get_not_installed(packages):
            """ This method checks if the packages have
            already been installed.
            """
            not_installed = []
            installed = []
            apt_list = subprocess.check_output(['apt', 'list'], stderr=subprocess.DEVNULL).decode('utf-8').split('\n')
            for line in apt_list:
                for pkg in packages:
                    if pkg == line.split('/')[0] and 'installed' not in line:
                        not_installed.append(pkg)
                    elif pkg == line.split('/')[0] and 'installed' in line:
                        installed.append(pkg)
            return not_installed, installed

        def apt_install(not_installed, installed):
            """ This method uses apt-get to install the package
            """
            if not isinstance(not_installed, list) or not isinstance(installed, list):
                return False
            Avalon.info('Packages already installed:')
            print(' '.join(installed))
            Avalon.info('Packages to be installed:')
            print(' '.join(not_installed))
            if Avalon.ask('Confirm installation:', False):
                subprocess.call('apt-get install -y {}'.format(' '.join(not_installed)), shell=True)
            else:
                Avalon.warning('Installation aborted')

        not_installed, installed = get_not_installed(packages)
        apt_install(not_installed, installed)


# /////////////////// Execution /////////////////// #

if __name__ == '__main__':
    try:
        icon()
        process_arguments()
        kobj = Kpm()
        if os.getuid() != 0:
            Avalon.error('This program must be run as root!')
            exit(0)
        if not kobj.internet_connected():
            exit(0)

        if args.force_upgrade:
            Avalon.info('Force upgrading KPM from GitHub')
            upgrade_kpm()

        check_version()

        Avalon.info('KPM initialized')
        if args.install_kpm:
            os.system('cp ' + os.path.abspath(__file__) + ' /usr/bin/kpm')  # os.rename throws an error when /tmp is in a separate partition
            os.system('chown root: /usr/bin/kpm')
            os.system('chmod 755 /usr/bin/kpm')
            Avalon.info('KPM successfully installed')
            Avalon.info('Now you can type \'kpm\' to start KPM')
            exit(0)
        elif args.xinstall:
            packages = args.xinstall.split(',')
            kobj.xinstall(packages)
        elif args.install:
            packages = args.install.split(',')
            empty_packages = False
            for pkg in packages:
                if len(pkg) == 0:
                    empty_packages = True
            if empty_packages:
                Avalon.error('Please provide valid package names!')
                exit(0)
            for pkg in packages:
                Avalon.info('Installing package: ' + pkg)
                os.system('apt-get install ' + pkg)
        elif args.search:
            Avalon.info('Searching in PT cache')
            os.system(('apt-cache search ' + args.search + ' | grep --color=auto -E "^|"' + args.search + '"'))
        elif args.version:
            Avalon.info('Getting versions for package ' + args.version)
            os.system('apt-cache madison ' + args.version)
        elif args.autoremove:
            Avalon.info('Auto-removing unused packages from system')
            os.system('apt-get autoremove')
        else:
            kobj.upgrade_all()
            Avalon.debug_info('Checking for unused packages')
            if kobj.autoremove_available():
                if Avalon.ask('Remove useless packages?', True):
                    kobj.autoremove()
            else:
                Avalon.info('No unused packages found')
            Avalon.info('Erasing old downloaded archive files')
            kobj.autoclean()
        Avalon.info('KPM finished')
    except KeyboardInterrupt:
        Avalon.warning('Aborting')
