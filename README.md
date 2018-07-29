# K4YT3X Package Manager

## Current Update (Version 1.6.2, July 28, 2018)

- KPM now uses requests instead of urllib

## What is KPM?

**For short, KPM makes apt upgrading simple and fully automatic.**

KPM stands for "K4YT3X Package Manager". I developed this program to make using apt easier and safer, especially when using "apt update && apt upgrade -y && apt dist-upgrade -y". It is unsafe to use the command above since under some situations, unsafe repos can remove packages form your computer. Sometimes these removals can be critically harmful to your system, such as removing gnome desktop entirely.

KPM automatically checks packages before committing any upgrading actions. An upgrade that will  not cause any removal of other packages will be considered "safe" and kpm will automatically start upgrading. An upgrade that will cause removals will be considered "unsafe" and will require the user's confirmation before taking any actions.

After upgrading, it will detect if there are automatically installed packages that are not needed anymore, and prompt to ask if the user wants to remove them (`apt autoremove`). It will also execute `apt autoclean` to erase old downloaded packages.

## Installation

```
$ git clone "https://github.com/K4YT3X/KPM.git"
$ cd KPM
$ sudo python3 kpm.py --install-kpm
```

That's it, now type 'kpm' to start your first automatic upgrade!

## Removal

Should be easy

```
$ sudo rm -f /usr/bin/kpm
```

## Usages

You only need to type `kpm` to launch automatic upgrade once KPM has been installed onto your system. The full help section is down below. You can also use the `-h` or `help` argument to show the help page.

```
usage: kpm.py [-h] [-i INSTALL] [-s SEARCH] [-v VERSION] [-a] [--install-kpm]
              [--force-upgrade]

optional arguments:
  -h, --help            show this help message and exit

ACTIONS:
  -i INSTALL, --install INSTALL
                        install package
  -s SEARCH, --search SEARCH
                        search for package in apt cache
  -v VERSION, --version VERSION
                        show package versions
  -a, --autoremove      APT autoremove extra packages
  --install-kpm         Install KPM to system
  --force-upgrade       Force replacing KPM with newest version
```
