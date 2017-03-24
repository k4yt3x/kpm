# KPM
### What is KPM?

KPM stands for "K4YT3X Package Manager". I developed this program to make using apt easier and safer, especially when using "apt update && apt upgrade -y && apt dist-upgrade -y". It is unsafe to use the command above since under some situations, unsafe repos can remove packages form your computer. Sometimes these removals can be critically harmful to your system, such as removing gnome desktop entirely.

KPM automatically checks packages before committing any upgrading actions. An upgrade that will  not cause any removal of other packages will be considered "safe" and kpm will automatically start upgrading. An upgrade that will cause removals will be considered "unsafe" and will require the user's confirmation before taking any actions.


#
### Install KPM
~~~~
$ git clone "https://github.com/K4YT3X/KPM.git"
$ cd KPM
$ sudo mv kpm.py /usr/bin/kpm
$ sudo chmod 755 /usr/bin/kpm
$ sudo chown root: /usr/bin/kpm
~~~~

That's it, now type 'kpm' to start your first automatic upgrade!

#
### Commands
Normal Update + Upgrade + Dist-Upgrade:
~~~~
$ sudo kpm
~~~~

Search for packages in APT cache:
~~~~
$ kpm -s [package]
~~~~

Install Package
~~~~
$ sudo kpm -i [package]
~~~~
