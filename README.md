# K4YT3X Package Manager

## 1.8.0 (September 17, 2019)

- Major code optimization
  - Better code format

## 1.7.5 (May 5, 2019)

- Updated `subprocess.Popen` to `subprocess.run`.
- Fixed grammar error (ouch).

## 1.7.3 (January 30, 2019)

- Updated error message handling when packages fail to upgrade.

## 1.7.2 (October 19, 2018)
- I know this is not wise but, updated for avalon framework 1.6.1.

![kpm_screenshot](https://user-images.githubusercontent.com/21986859/52021673-0bb34a00-24c4-11e9-8da2-108c20d83840.png)

## What is KPM?

**For short, KPM makes apt upgrading simple and fully automatic.**

KPM stands for "K4YT3X Package Manager". I developed this program to make using apt easier and safer, especially when using "apt update && apt upgrade -y && apt dist-upgrade -y". It is unsafe to use the command above since under some situations, unsafe repos can remove packages form your computer. Sometimes these removals can be critically harmful to your system, such as removing gnome desktop entirely.

KPM automatically checks packages before committing any upgrading actions. An upgrade that will  not cause any removal of other packages will be considered "safe" and kpm will automatically start upgrading. An upgrade that will cause removals will be considered "unsafe" and will require the user's confirmation before taking any actions.

After upgrading, it will detect if there are automatically installed packages that are not needed anymore, and prompt to ask if the user wants to remove them (`apt autoremove`). It will also execute `apt autoclean` to erase old downloaded packages.

## Installation

### Install Dependencies

```bash
$ sudo pip3 install avalon_framework
```

### Install KPM

#### Express Install

```bash
$ sudo curl https://raw.githubusercontent.com/K4YT3X/kpm/master/kpm.py -o /usr/bin/kpm && sudo chmod 755 /usr/bin/kpm && sudo chown root: /usr/bin/kpm
```

#### Regular Install

```
$ git clone "https://github.com/K4YT3X/kpm.git"
$ cd kpm
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
usage: kpm.py [-h] [-i INSTALL] [-s SEARCH] [-v VERSION] [-a] [-x XINSTALL]
              [--install-kpm] [--force-upgrade]

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
  -x XINSTALL, --xinstall XINSTALL
                        Install without marking already-installed packages as
                        manually installed
  --install-kpm         Install KPM to system
  --force-upgrade       Force replacing KPM with newest version
```
