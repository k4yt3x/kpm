# K4YT3X Package Manage
### What is KPM?
**For short, KPM makes apt upgrading simple and fully automatic.**

</br>

### Changelog:
#### Current Version: 1.6.1
1. Added autoclean after upgrading

</br>

#### Recent Changes:
1. Changed the method for detecting internet connection
1. Added internal documentation
1. Detect ubuntu source in non-ubuntu distributions
1. Added automatic installation for required package "dirmngr"
1. Added a second apt update after key importing
1. Added automatic update function
1. Changed apt interface from apt command to apt -get for more stable output

</br>


#### Full Description
KPM stands for "K4YT3X Package Manager". I developed this program to make using apt easier and safer, especially when using "apt update && apt upgrade -y && apt dist-upgrade -y". It is unsafe to use the command above since under some situations, unsafe repos can remove packages form your computer. Sometimes these removals can be critically harmful to your system, such as removing gnome desktop entirely.

KPM automatically checks packages before committing any upgrading actions. An upgrade that will  not cause any removal of other packages will be considered "safe" and kpm will automatically start upgrading. An upgrade that will cause removals will be considered "unsafe" and will require the user's confirmation before taking any actions.

</br>

### Install KPM
~~~~
$ git clone "https://github.com/K4YT3X/KPM.git"
$ cd KPM
$ sudo python3 kpm.py --installkpm
~~~~

That's it, now type 'kpm' to start your first automatic upgrade!

</br>

### Remove KPM
Should be easy
~~~~
$ sudo rm -f /usr/bin/kpm
~~~~

</br>

### Usage
~~~~
$ sudo kpm                 # Normal Upgrade and Dist-upgrade
$ sudo kpm -i [package]    # install package
$ sudo kpm -s [name]       # search for packages in apt cache
$ sudo kpm -a              # executes "apt autoremove"
$ sudo kpm -v              # prints kpm version
$ sudo kpm --installkpm    # install kpm to system
~~~~
