# K4YT3X Package Manager

KPM performs APT full upgrade automatically. It has the following workflow:

1. Update APT cache
1. Check if upgrades are available
1. Check if upgrades are safe
   - An upgrade is deemed unsafe it it removes any packages
   - Manual confirmation is required to commence unsafe upgrades
1. Check and purge automatically installed unused packages
1. Check and purge residual configuration files
1. Remove old downloaded archives

![kpm](https://user-images.githubusercontent.com/21986859/99754993-8d34fb80-2ae1-11eb-879c-aa40b3ddcd21.png)\
*KPM in action*

## Installation

```shell
git clone https://github.com/k4yt3x/kpm.git

# install Python dependencies
sudo pip3 install -Ur kpm/src/requirements.txt

# install kpm script into system
sudo python3 kpm/src/kpm.py --install_kpm

# you may also move the file manually
sudo mv kpm/src/kpm.py /usr/local/bin/kpm
sudo chown root:root /usr/local/bin/kpm
sudo chmod 755 /usr/local/bin/kpm
```

## Removal

KPM does not produce any cache files or configuration files. Simply remove the script from `/usr/local/bin`.

```shell
sudo rm /usr/local/bin/kpm
```

## Full Usages

Issuing the command `kpm` without any arguments will launch automatic upgrade. The usages can also be printed via issuing the command `kpm -h` or `kpm --help`.

```console
usage: kpm.py [-h] [-i] [--install_kpm] [--force_upgrade]

optional arguments:
  -h, --help            show this help message and exit

ACTIONS:
  -i, --ignore_connectivity
                        ignore internet connectivity check results
  --install_kpm         install KPM to system
  --force_upgrade       force replacing KPM with newest version
```
