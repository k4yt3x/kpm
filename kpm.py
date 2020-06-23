#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: K4YT3X Package Manager
Author: K4YT3X
Date Created: March 24, 2017
Last Modified: June 23, 2020

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt

(C) 2017-2020 K4YT3X

Description: KPM is an automatic apt management system
    simply use command "kpm" to automatically update apt cache,
    upgrade all upgradeable packages safely. It is also capable
    of calling more apt functions easily
"""

# built-in imports
import argparse
import contextlib
import distro
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import traceback


# third-party imports
from avalon_framework import Avalon
import requests

VERSION = '1.8.3'

# constants
GITHUB_KPM_FILE = 'https://raw.githubusercontent.com/k4yt3x/kpm/master/kpm.py'
GPG_KEY_SERVER = 'hkp://keys.gnupg.net'
INTERNET_TEST_PAGE = 'http://detectportal.firefox.com/success.txt'
KPM_PATH = pathlib.Path('/usr/local/bin/kpm')


def upgrade_kpm():
    """ upgrade KPM

    Upgrades KPM by downloading the latest version from GitHub.
    Replaces the current file being executed.
    """
    try:

        # get python script web page
        kpm_request = requests.get(GITHUB_KPM_FILE)
        if kpm_request.status_code != requests.codes.ok:
            kpm_request.raise_for_status()

        # write web page content to file
        with pathlib.Path(__file__).open(mode='wb') as kpm_file:
            kpm_file.write(kpm_request.content)

        Avalon.info('KPM has been updated successfully')
        Avalon.info('Please relaunch KPM')
        sys.exit(0)

    except Exception:
        Avalon.error('There was an error updating KPM')
        Avalon.warning('You might have to reinstall KPM manually')


def check_version():
    """ check if KPM is up-to-date

    Check if KPM is up to date with the the newest
    version on GitHub. Prompt the user to upgrade if
    the local version is not the newest.
    """
    # get version number of KPM on GitHub
    Avalon.debug_info('Checking KPM Version')
    for line in requests.get(GITHUB_KPM_FILE).text.split('\n'):
        if 'VERSION = ' in line:
            server_version = line.split(' ')[-1].replace('\'', '')
            break
    Avalon.debug_info(f'Server version: {server_version}')

    # if the server version is newer than local version
    if server_version > VERSION:
        Avalon.info('Here\'s a newer version of KPM!')
        if Avalon.ask('Update to the newest version?', True):
            upgrade_kpm()
        else:
            Avalon.warning('Ignoring update')
    else:
        Avalon.debug_info('KPM is already on the newest version')


def process_arguments():
    """ This function takes care of all arguments
    """
    parser = argparse.ArgumentParser()
    action_group = parser.add_argument_group('ACTIONS')
    action_group.add_argument('-x', '--xinstall', help='install without marking already-installed packages as manually installed', action='store')
    action_group.add_argument('-m', '--madison', help='list all versions of a package', action='store')
    action_group.add_argument('-s', '--search', help='search in APT cache with highlight', action='store')
    action_group.add_argument('-i', '--ignore_connectivity', help='ignore internet connectivity check results', action='store_true')
    action_group.add_argument('--install_kpm', help='install KPM to system', action='store_true')
    action_group.add_argument('--force_upgrade', help='force replacing KPM with newest version', action='store_true')

    return parser.parse_args()


def print_icon():
    print(f'''{Avalon.FM.BD}{Avalon.FG.R}  _  __  {Avalon.FG.G} ____   {Avalon.FG.M} __  __ {Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | |/ /  {Avalon.FG.G}|  _ \\  {Avalon.FG.M}|  \\/  |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | \' /   {Avalon.FG.G}| |_) | {Avalon.FG.M}| |\\/| |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | . \\   {Avalon.FG.G}|  __/  {Avalon.FG.M}| |  | |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} |_|\\_\\  {Avalon.FG.G}|_|     {Avalon.FG.M}|_|  |_|{Avalon.FG.W}
{Avalon.FM.BD}\n K4YT3X Package Manager {Avalon.FG.LY}{Avalon.FM.BD}{VERSION}{Avalon.FM.RST}\n''')


class Kpm:

    def __init__(self):
        self.import_list = []

    @staticmethod
    def import_keys(keys: list) -> int:
        """ import GPG keys

        Arguments:
            keys {list} -- list of key IDs to imports

        Returns:
            int -- return code of subprocess execution
        """
        execute = [
            'apt-key',
            'adv',
            '--keyserver',
            GPG_KEY_SERVER,
            '--recv'
        ]

        execute.extend(keys)
        return subprocess.call(execute)

    @staticmethod
    def install(packages: list) -> int:
        """ install packages with APT

        Arguments:
            packages {list} -- list of packages to install

        Returns:
            int -- APT process return code
        """
        execute = [
            'apt-get',
            'install',
        ]

        execute.extend(packages)
        return subprocess.call(execute).returncode

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
                if 'ubuntu.com' in line and distro.linux_distribution()[0] != 'Ubuntu' and line.replace(' ', '')[0] != '#':
                    Avalon.warning('Ubuntu source detected in source.list!')
                    Avalon.warning('Continue upgrading might cause severe consequences!')

                    if Avalon.ask('Are you sure that you want to continue?', False):
                        break
                    else:
                        Avalon.warning('Aborting system upgrade..')
                        sys.exit(0)
        self.update()
        Avalon.info('APT cache updated')

        if len(self.import_list) != 0:
            if Avalon.ask('Detected unimported keys, import?', True):
                if shutil.which('dirmngr') is None:
                    Avalon.warning('dirmngr Not installed')
                    Avalon.warning('It is required for importing keys')

                    # ask if user wants to install dirmngr
                    if Avalon.ask('Install Now?'):
                        self.install('dirnmgr')

                        # check dirmngr after package installation
                        if isinstance(shutil.which('dirmngr'), str):
                            Avalon.info('Installation successful')
                            self.import_keys(self.import_list)
                            Avalon.info('Keys imported')
                            Avalon.info('Updating APT cache after key importing')
                            self.update()
                        else:
                            Avalon.error('Installation Failed')
                            Avalon.error('Please check your settings')
                            Avalon.warning('dirmngr not available. Continuing without importing keys')
                    else:
                        Avalon.warning('dirmngr not available')
                        Avalon.warning('Continuing without importing keys')

                else:
                    self.import_keys(self.import_list)
                    Avalon.info('Keys imported')
                    Avalon.info('Updating APT cache after key importing')
                    self.update()

            # Second update after keys are imported
            self.update()

        # if there are no upgrades available
        Avalon.debug_info('Checking package updates')
        if self.no_upgrades():
            Avalon.info('No upgrades available')

        # if upgrades are available
        else:
            Avalon.debug_info('Checking if full upgrade is safe')

            # if upgrade is safe, use -y flag on apt-get full-upgrade
            # otherwise, let user confirm the upgrade
            if self.full_upgrade_safe():
                Avalon.info('Full upgrade is safe')
                Avalon.info('Starting APT full upgrade')
                self.full_upgrade()
            else:
                Avalon.warning('Full upgrade is NOT safe')
                Avalon.warning('Requiring human confirmation')
                self.manual_full_upgrade()

    @staticmethod
    def full_upgrade_safe() -> bool:
        """ check if dist-upgrade safe

        This method checks if dist-upgrade will remove
        packages from the system. If yes, then it is considered
        unsafe.

        Returns:
            bool -- True if safe to upgrade
        """
        execute = [
            'apt-get',
            'full-upgrade',
            '-s'
        ]
        output = subprocess.run(execute, stdout=subprocess.PIPE).stdout.decode().split('\n')
        for line in output:
            with contextlib.suppress(IndexError):
                if line.replace('and', ',').replace(' ', '').split(',')[2] == '0toremove':
                    return True
        return False

    def update(self):
        """ update APT cache
        """
        process = subprocess.Popen(['apt-get', 'update'], stdout=subprocess.PIPE)

        # create buffer string to store command output
        output = ''

        # read output into buffer string
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

    @staticmethod
    def autoclean():
        """ erase old downloaded packages automatically
        """
        execute = [
            'apt-get',
            'autoclean'
        ]
        return subprocess.call(execute)

    @staticmethod
    def full_upgrade():
        execute = [
            'apt-get',
            'full-upgrade',
            '-y'
        ]
        return subprocess.call(execute)

    @staticmethod
    def manual_full_upgrade():
        execute = [
            'apt-get',
            'full-upgrade',
        ]
        return subprocess.call(execute)

    @staticmethod
    def list_upgrades():
        execute = [
            'apt',
            'list',
            '--upgradable'
        ]
        return subprocess.call(execute)

    @staticmethod
    def no_upgrades() -> bool:
        """ check if no upgrades are available

        Determine if there are no upgrades available

        Returns:
            bool -- True if there are packages available
        """
        output = subprocess.run(['apt-get', 'full-upgrade', '-s'], stdout=subprocess.PIPE).stdout.decode().split('\n')
        for line in output:
            parsed_line = line.replace('and', ',').replace(' ', '').split(',')
            if parsed_line[0] == '0upgraded' and parsed_line[1] == '0newlyinstalled':
                if parsed_line[3] != '0notupgraded.':
                    Avalon.warning('Some packages are not upgraded')
                    Avalon.warning('Attempting to print messages from APT:')
                    subprocess.call(['apt', 'upgrade', '-s'])
                return True
        return False

    @staticmethod
    def autoremove() -> int:
        """ remove packages that are not needed automatically

        Returns:
            int -- remove unused packages
        """
        execute = [
            'apt-get',
            'autoremove',
            '--purge'
        ]
        return subprocess.call(execute)

    @staticmethod
    def autoremove_available() -> bool:
        """ determines if there's autoremove available

        Returns:
            bool -- True if autoremove is available
        """
        execute = [
            'apt-get',
            'install',
            '-s'
        ]

        output = subprocess.run(execute, stdout=subprocess.PIPE).stdout.decode()
        if 'no longer required' in output:
            return True
        else:
            return False

    @staticmethod
    def xinstall(packages: list):
        """ install only packages that are not installed

        By using the xinstall function to install packages,
        already-installed packages will not get marked as
        manually installed by APT.

        Arguments:
            packages {list} -- list of packages to install
        """
        not_installed = []
        installed = []

        # get a list of all locally installed packages
        apt_list = subprocess.run(['apt', 'list'], stderr=subprocess.DEVNULL).stdout.decode().split('\n')
        for line in apt_list:
            for package in packages:
                if package == line.split('/')[0] and 'installed' not in line:
                    not_installed.append(package)
                elif package == line.split('/')[0] and 'installed' in line:
                    installed.append(package)

        Avalon.info('Packages already installed:')
        print(' '.join(installed))

        Avalon.info('Packages to be installed:')
        print(' '.join(not_installed))

        execute = [
            'apt-get',
            'install',
            '-s'
        ]

        execute.extend(not_installed)

        Avalon.info('Launching a dry-run')
        subprocess.call(execute)

        if Avalon.ask('Confirm installation:', False):

            # swap -s flag with -y for actual installation
            execute[execute.index('-s')] = '-y'
            subprocess.call(execute)

        else:
            Avalon.warning('Installation aborted')


def internet_connected() -> bool:
    """ detect if there's valid internet connectivity

    Tries to fetch a web page with known content to see
    if there's a valid internet connection.

    Returns:
        bool -- True if valid internet connection is available
    """

    try:
        Avalon.debug_info(f'Fetching: {INTERNET_TEST_PAGE}')
        success_page = requests.get(INTERNET_TEST_PAGE)
        if success_page.text != 'success\n':
            return False
        else:
            return True
    except Exception:
        return False


# -------------------- Execution

if __name__ != '__main__':
    Avalon.error('This file cannot be imported as a library')
    raise ImportError('file cannot be imported')

# print KPM icon
print_icon()

# parse command line arguments
args = process_arguments()

try:
    # create KPM object
    kobj = Kpm()
    Avalon.info('KPM initialized')

    # if -s, --search specified
    if args.search:
        Avalon.info('Searching in APT cache')
        subprocess.call(f'apt-cache search {args.search} | egrep --color=auto "^|{args.search}"', shell=True)
        sys.exit(0)

    # if -m, --madison specified
    elif args.madison:
        Avalon.info(f'Getting versions for package {args.madison}')
        subprocess.call(f'apt-cache madison {args.madison}', shell=True)
        sys.exit(0)

    # privileged section
    # check user privilege
    if os.getuid() != 0:
        Avalon.error('This program must be run as root!')
        sys.exit(1)

    # if --install_kpm
    if args.install_kpm:
        # move the current file to defined binary path
        shutil.move(pathlib.Path(__file__), KPM_PATH)

        # change owner and permission of the file
        os.chown(KPM_PATH, 0, 0)
        KPM_PATH.chmod(0o755)

        Avalon.info('KPM successfully installed')
        Avalon.info('Now you can type \'kpm\' to start KPM')
        sys.exit(0)

    # check internet connectivity
    if args.ignore_connectivity:
        Avalon.warning('Skipping connectivity check')
    else:
        Avalon.info('Checking internet connectivity')
        if not internet_connected():
            Avalon.error('No valid internet connectivity detected')
            sys.exit(1)

    # if --force_upgrade
    if args.force_upgrade:
        Avalon.info('Force upgrading KPM from GitHub')
        upgrade_kpm()
        sys.exit(0)

    check_version()

    # if -x, --xinstall specified
    if args.xinstall:
        packages = args.xinstall.split(',')
        kobj.xinstall(packages)

    # if no arguments are given
    else:
        kobj.upgrade_all()
        Avalon.debug_info('Checking for unused packages')

        # check if there are any unused packages
        if kobj.autoremove_available():
            if Avalon.ask('Remove useless packages?', True):
                kobj.autoremove()
        else:
            Avalon.info('No unused packages found')

        # apt autoclean
        Avalon.info('Erasing old downloaded archive files')
        kobj.autoclean()

except KeyboardInterrupt:
    Avalon.warning('Aborting')

except Exception:
    Avalon.error('Error caught during execution')
    traceback.print_exc()

finally:
    Avalon.info('KPM finished')
