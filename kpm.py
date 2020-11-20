#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: K4YT3X Package Manager
Author: K4YT3X
Date Created: March 24, 2017
Last Modified: November 19, 2020

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
import shutil
import subprocess
import sys
import traceback

# third-party imports
from avalon_framework import Avalon
import requests

VERSION = "1.10.0"

# global constants
INTERNET_TEST_PAGE = "http://detectportal.firefox.com/success.txt"
KPM_PATH = pathlib.Path("/usr/local/bin/kpm")


def upgrade_kpm():
    """ upgrade KPM

    Upgrades KPM by downloading the latest version from GitHub.
    Replaces the current file being executed.
    """
    try:

        latest_json = requests.get(
            "https://api.github.com/repos/k4yt3x/kpm/releases/latest"
        ).json()

        for asset in latest_json["assets"]:
            if latest_json["assets"][asset]["name"] == "kpm.py":
                latest_version_url = latest_json["assets"][asset][
                    "browser_download_url"
                ]
                break
        else:
            Avalon.warning("Unable to find the latest version's download URL")
            return

        # get python script web page
        kpm_request = requests.get(latest_version_url)
        if kpm_request.status_code != requests.codes.ok:
            kpm_request.raise_for_status()

        # write web page content to file
        with pathlib.Path(__file__).open(mode="wb") as kpm_file:
            kpm_file.write(kpm_request.content)

        Avalon.info("KPM has been updated successfully")
        Avalon.info("Please relaunch KPM")
        sys.exit(0)

    except Exception as e:
        Avalon.error("There was an error updating KPM")
        Avalon.warning("You might have to reinstall KPM manually")
        raise e


def check_version():
    """ check if KPM is up-to-date

    Check if KPM is up to date with the the newest
    version on GitHub. Prompt the user to upgrade if
    the local version is not the newest.
    """
    # get version number of KPM on GitHub
    Avalon.info("Checking KPM's Version")
    latest_json = requests.get(
        "https://api.github.com/repos/k4yt3x/kpm/releases/latest"
    ).json()
    latest_version = latest_json["tag_name"]
    Avalon.debug_info(f"Server version: {latest_version}")

    # if the server version is newer than local version
    if latest_version > VERSION:
        Avalon.info(f"There is a newer version of KPM available ({latest_version})")
        if Avalon.ask("Update to the newest version?", True):
            upgrade_kpm()
        else:
            Avalon.warning("Skipping the upgrade for now")
    else:
        Avalon.debug_info(f"KPM is already on the newest version ({VERSION})")


def parse_arguments():
    """ this function parses command line arguments
    """
    parser = argparse.ArgumentParser()
    action_group = parser.add_argument_group("ACTIONS")
    action_group.add_argument(
        "-i",
        "--ignore_connectivity",
        help="ignore internet connectivity check results",
        action="store_true",
    )
    action_group.add_argument(
        "--install_kpm", help="install KPM to system", action="store_true"
    )
    action_group.add_argument(
        "--force_upgrade",
        help="force replacing KPM with newest version",
        action="store_true",
    )

    return parser.parse_args()


def print_icon():
    print(
        f"""{Avalon.FM.BD}{Avalon.FG.R}  _  __  {Avalon.FG.G} ____   {Avalon.FG.M} __  __ {Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | |/ /  {Avalon.FG.G}|  _ \\  {Avalon.FG.M}|  \\/  |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | \' /   {Avalon.FG.G}| |_) | {Avalon.FG.M}| |\\/| |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} | . \\   {Avalon.FG.G}|  __/  {Avalon.FG.M}| |  | |{Avalon.FG.W}
{Avalon.FM.BD}{Avalon.FG.R} |_|\\_\\  {Avalon.FG.G}|_|     {Avalon.FG.M}|_|  |_|{Avalon.FG.W}
{Avalon.FM.BD}\n K4YT3X Package Manager {Avalon.FG.LY}{Avalon.FM.BD}{VERSION}{Avalon.FM.RST}\n"""
    )


class Kpm:
    def __init__(self):
        self.import_list = []

    @staticmethod
    def install(packages: list) -> int:
        """ install packages with APT

        Arguments:
            packages {list} -- list of packages to install

        Returns:
            int -- APT process return code
        """
        execute = [
            "/usr/bin/apt-get",
            "install",
        ]

        execute.extend(packages)
        return subprocess.call(execute)

    def upgrade_full(self):
        """ upgrade all packages

        This method checks if there are packages
        available for updating and update the packages
        if updating them won't remove any packages from
        the system. Often times when a bad source is added
        to the system, APT tends to remove a number of packages
        from the system when upgrading which is very risky.
        """
        Avalon.info("Starting automatic upgrade")
        Avalon.info("Updating APT cache")
        with open("/etc/apt/sources.list", "r") as aptlist:
            for line in aptlist:
                if (
                    "ubuntu.com" in line
                    and distro.linux_distribution()[0] != "Ubuntu"
                    and line.replace(" ", "")[0] != "#"
                ):
                    Avalon.warning("Ubuntu source detected in source.list!")
                    Avalon.warning(
                        "Continue upgrading might cause severe consequences!"
                    )

                    if Avalon.ask("Are you sure that you want to continue?", False):
                        break
                    else:
                        Avalon.warning("Aborting system upgrade..")
                        sys.exit(0)
        self.update()
        Avalon.info("APT cache updated")

        if len(self.import_list) != 0:
            Avalon.ask(f"Detected un-imported keys: {' '.join(self.import_list)}")

        # if there are no upgrades available
        Avalon.info("Checking package updates")
        if self.no_upgrades():
            Avalon.debug_info("No upgrades available")

        # if upgrades are available
        else:
            Avalon.info("Checking if full upgrade is safe")

            # if upgrade is safe, use -y flag on apt-get full-upgrade
            # otherwise, let user confirm the upgrade
            if self.full_upgrade_safe():
                Avalon.debug_info("Full upgrade is safe")
                Avalon.info("Starting APT full upgrade")
                self.full_upgrade()
            else:
                Avalon.warning("Full upgrade is NOT safe")
                Avalon.warning("Requiring human confirmation")
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
        execute = ["/usr/bin/apt-get", "full-upgrade", "-s"]
        output = (
            subprocess.run(execute, stdout=subprocess.PIPE).stdout.decode().split("\n")
        )
        for line in output:
            with contextlib.suppress(IndexError):
                if (
                    line.replace("and", ",").replace(" ", "").split(",")[2]
                    == "0toremove"
                ):
                    return True
        return False

    def update(self):
        """ update APT cache
        """
        process = subprocess.Popen(
            ["/usr/bin/apt-get", "update"], stdout=subprocess.PIPE
        )

        # create buffer string to store command output
        output = ""

        # read output into buffer string
        for character in iter(lambda: process.stdout.read(1), ""):
            if not character:
                break
            sys.stdout.write(character.decode())
            output += character.decode()

        for line in output.split("\n"):
            if "NO_PUBKEY" in line:
                self.import_list.append(line.split(" ")[-1].replace("\n", ""))
            elif "EXPKEYSIG" in line:
                self.import_list.append(line.split("EXPKEYSIG ")[1].split(" ")[0])

    @staticmethod
    def autoclean():
        """ erase old downloaded packages automatically
        """
        execute = ["/usr/bin/apt-get", "autoclean"]
        return subprocess.call(execute)

    @staticmethod
    def full_upgrade():
        execute = ["/usr/bin/apt-get", "full-upgrade", "-y"]
        return subprocess.call(execute)

    @staticmethod
    def manual_full_upgrade():
        execute = [
            "/usr/bin/apt-get",
            "full-upgrade",
        ]
        return subprocess.call(execute)

    @staticmethod
    def list_upgrades():
        execute = ["/usr/bin/apt", "list", "--upgradable"]
        return subprocess.call(execute)

    @staticmethod
    def no_upgrades() -> bool:
        """ check if no upgrades are available

        Determine if there are no upgrades available

        Returns:
            bool -- True if there are packages available
        """
        output = (
            subprocess.run(
                ["/usr/bin/apt-get", "full-upgrade", "-s"], stdout=subprocess.PIPE
            )
            .stdout.decode()
            .split("\n")
        )
        for line in output:
            parsed_line = line.replace("and", ",").replace(" ", "").split(",")
            if parsed_line[0] == "0upgraded" and parsed_line[1] == "0newlyinstalled":
                if parsed_line[3] != "0notupgraded.":
                    Avalon.warning("Some packages are not upgraded")
                    Avalon.warning("Attempting to print messages from APT:")
                    subprocess.call(["/usr/bin/apt", "upgrade", "-s"])
                return True
        return False

    @staticmethod
    def autoremove() -> int:
        """ remove packages that are not needed automatically

        Returns:
            int -- remove unused packages
        """
        execute = ["/usr/bin/apt-get", "autoremove", "--purge"]
        return subprocess.call(execute)

    @staticmethod
    def autoremove_available() -> bool:
        """ determines if there's autoremove available

        Returns:
            bool -- True if autoremove is available
        """
        execute = ["/usr/bin/apt-get", "install", "-s"]

        output = subprocess.run(execute, stdout=subprocess.PIPE).stdout.decode()
        if "no longer required" in output:
            return True
        else:
            return False

    @staticmethod
    def dpkg_purge_residual_configs(packages: list):
        """ use dpkg to remove residual configs of the given packages

        Args:
            packages (list): a list of names of packages
        """
        Avalon.debug_info("Purging residual configuration files")
        subprocess.run(["/usr/bin/dpkg", "--purge"] + packages)

    @staticmethod
    def get_dpkg_residual_configs() -> list:
        """ get a list of packages with residual configs

        Returns:
            list: a list of packages with residual configs
        """
        execute = ["/usr/bin/dpkg", "-l"]
        output = subprocess.run(execute, stdout=subprocess.PIPE).stdout.decode()
        rc_packages = []
        for line in output.split("\n"):
            if line.startswith("rc"):
                rc_packages.append(line.split()[1])
        return rc_packages


def internet_connected() -> bool:
    """ detect if there's valid internet connectivity

    Tries to fetch a web page with known content to see
    if there's a valid internet connection.

    Returns:
        bool -- True if valid internet connection is available
    """

    try:
        Avalon.debug_info(f"Fetching: {INTERNET_TEST_PAGE}")
        success_page = requests.get(INTERNET_TEST_PAGE)
        if success_page.text != "success\n":
            return False
        else:
            return True
    except Exception:
        return False


# -------------------- Execution

if __name__ != "__main__":
    Avalon.error("This file cannot be imported as a library")
    raise ImportError("file cannot be imported")

# parse command line arguments
args = parse_arguments()

# print KPM icon
print_icon()

try:
    # create KPM object
    kpm = Kpm()
    Avalon.debug_info("KPM initialized")

    # privileged section
    # check user privilege
    if os.getuid() != 0:
        Avalon.error("This program must be run as root")
        sys.exit(1)

    # if --install_kpm
    if args.install_kpm:
        # copy the current file to defined binary path
        shutil.copy(pathlib.Path(__file__), KPM_PATH)

        # change owner and permission of the file
        os.chown(KPM_PATH, 0, 0)
        KPM_PATH.chmod(0o755)

        Avalon.info("KPM successfully installed")
        Avalon.info("Now you can type 'kpm' to start KPM")
        sys.exit(0)

    # check internet connectivity
    if args.ignore_connectivity:
        Avalon.warning("Skipping connectivity check")
    else:
        Avalon.info("Checking internet connectivity")
        if not internet_connected():
            Avalon.error("No valid internet connectivity detected")
            sys.exit(1)

    # if --force_upgrade
    if args.force_upgrade:
        Avalon.info("Commencing forced upgrade")
        upgrade_kpm()
        sys.exit(0)

    # check for newer versions of KPM
    check_version()

    # commence APT full upgrade
    kpm.upgrade_full()

    # check if there are any unused packages
    Avalon.info("Checking for unused packages")
    if kpm.autoremove_available():
        if Avalon.ask("Remove automatically installed unused packages?", True):
            kpm.autoremove()
    else:
        Avalon.debug_info("No unused packages found")

    # check if there are any residual configuration files
    Avalon.info("Checking for residual configuration files")
    rc_packages = kpm.get_dpkg_residual_configs()

    if len(rc_packages) == 0:
        Avalon.debug_info("No residual configuration files found")
    else:
        Avalon.debug_info(
            f"Packages with residual configuration files: {' '.join(rc_packages)}"
        )
        if Avalon.ask("Purge residual configuration files?", True):
            kpm.dpkg_purge_residual_configs(rc_packages)

    # apt autoclean
    Avalon.info("Erasing old downloaded archive files")
    kpm.autoclean()

except KeyboardInterrupt:
    Avalon.warning("Aborting")

except Exception:
    Avalon.error("Error caught during execution")
    traceback.print_exc()

finally:
    Avalon.info("KPM finished")
