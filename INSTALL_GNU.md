## Font Bakery Install Instructions for GNU+Linux

To install:

    pip install fontbakery;
    
To upgrade:

    pip install --upgrade fontbakery;

#### Additional Dependencies

##### FontForge

From a PPA on Ubuntu:

    sudo add-apt-repository --yes ppa:fontforge/fontforge;
    sudo apt-get update -qq;
    sudo apt-get install python-fontforge

##### Remote ftxvalidator

The script available at `prebuilt/workarounds/ftxvalidator/ssh-implementation/ftxvalidator` let's you execute the Mac OS tool `ftxvalidator` on a remote host. It is designed as a drop in replacement to be put in your `/usr/local/bin` directory.

In order to use it you must also add your client's ssh public key to `.ssh/authorized_keys` on the remote machine.

