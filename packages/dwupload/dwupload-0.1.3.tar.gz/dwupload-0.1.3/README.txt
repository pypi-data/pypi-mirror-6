dwupload README
==================

The dwupload program is a Demandware cartridge file watcher. The script watches the file system and synchronizes
files with your sandbox via webdav. The script assumes you are watching from the cartridges root path e.g.
/some/path/cartridges/ this path would then contain your dw cartridges below.

The script assumes that you have all your cartridges in one folder, which may change depending on use cases. Currently
for my use case our git repository contains all of our cartridges in one folder.

If the cartridge path is not set correctly the program can wipe all the files on your sandbox. To fix this simply run
a clean using Demandware Studio and then try fixing the root watch path. You may also run into issues if both Demandware
Studio and the dwupload script are both running, but I haven't had a problem so far.

This script has been tested on both 10.8.5 and Windows XP/7. Your mileage may vary.


Getting Started
---------------

 * Install Python 2.7 if it's not already installed
 * Install setuptools
 * Run python setup.py install
 * Create a configuration file there is an example in the dwupload package.
    * On unix based systems you can create .dwsettings in your home folder. This might work on windows, but has not been tested
 * If you have .dwsettings just run dwupload to start the file system watcher.
    * If you do not have .dwsettings you can specify the -c flag to supply the path to the config file
    * Alternatively you can add the DWUPLOAD_CONFIG_PATH environment variable so you do not have to specify the config path every time
 * Use dwupload -h to see the program's help text
