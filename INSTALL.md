# Installation instructions

This documents is step by step instruction how to setup development and production environment. As long as project in development stage production part subject to change.

## Requirements

You need to have installed:

- python 2.7.x
- virtualenv http://www.virtualenv.org/en/latest/
- make
- C-code compiler
- libevent
- fontforge (including its python module)
- ttfautohint
- Redis

### Mac OS X

If you use Mac OS X, a convenient way to install such UNIX software is with [HomeBrew](http://mxcl.github.io/homebrew/).

Install HomeBrew and then run these commands in the Terminal:

```sh
    # Use HomeBrew to install dependencies
    brew install python sqlite libevent fontforge ttfautohint redis;
    # To have launchd start redis at login:
    ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents;
    # Start redis now:
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist;
    # Confirm easy_install is available:
    which easy_install-2.7;
    # /usr/local/share/python/easy_install-2.7
    # Use easy_install to install pip, a better Python package manager
    sudo easy_install-2.7 -U pip;
    # Use easy_install to install virtualenv
    sudo easy_install-2.7 -U virtualenv;
    # Set up a pip download cache
    echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
    mkdir ~/.pip_download_cache;
```

### Fedora

TODO: package ttfautohint for Fedora

```sh
    # Use yum to install dependencies
    sudo yum install -y python-virtualenv python sqlite sqlite-devel libevent libevent-devel fontforge redis mercurial git;
    # install ttfautohint from git
    git clone git://repo.or.cz/ttfautohint.git;
    cd ttfautohint;
    ./bootstrap;
    ./configure --with-doc=no;
    sudo make install;
    # Start redis now:
    sudo /etc/init.d/redis start;
    # Set up a pip download cache
    echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
    mkdir ~/.pip_download_cache;
```

### Debian & Ubuntu

```sh
    # Use yum to install dependencies
    sudo apt-get install -y build-essential python python-virtualenv python-pip sqlite libsqlite3-dev libevent-2.0-5 libevent-dev fontforge redis-server curl default-jdk git mercurial;
    # install ttfautohint from git
    git clone git://repo.or.cz/ttfautohint.git;
    cd ttfautohint;
    ./bootstrap;
    ./configure --with-doc=no;
    sudo make install;
    # Start redis now:
    sudo /etc/init.d/redis-server start;
    # Set up a pip download cache
    echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
    mkdir ~/.pip_download_cache;
```

Now your system should be ready.

## Installation

Installing Font Bakery is easy. It requires some other programs, but does not install its own dependencies into your system. Most packages are installed into the `venv` directory.

First make a new 'src' folder for source code in your home directory, if it doesn't yet exist:

    mkdir ~/src;

Clone Google Font Directory Mercurial Repository from Google Code into new folder in your home directory:

    hg clone https://code.google.com/p/googlefontdirectory/ ~/src/googlefontdirectory;

Clone code from github into new folder:

    git clone https://github.com/xen/fontbakery.git ~/src/fontbakery;

Build and copy the Google Font Directory lint.jar tool into the fontbakery/scripts directory. This assumed you have

    which javac;
    # /usr/bin/javac
    cd ~/src/googlefontdirectory/tools/lint/;
    ant lint-jar;
    cp -pa ~/googlefontdirectory/tools/lint/dist/lint.jar ~/src/fontbakery/scripts/;

Then run setup:

    cd ~/src/fontbakery;
    make setup;

Wait some time and watch everything being installed.

NB: As `fontforge` can't be installed using pip, and is installed into your system python's site packaged make sure that
default python interpreter (`which python`) is the same where you installed `fontforge` and other dependencies.

**Optional step**: Make your own `local.cfg` based on `local.example.cfg`. You can use this example:

    GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
    GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'
    SQLALCHEMY_ECHO = True

Github application info is for demo use only. You can [make your own](https://github.com/settings/applications/new). Default values for URL `http://localhost:5000/`, callback URL `http://localhost:5000/auth/callback`.

Finally, initialise the database:

    make init;

Now see the running instructions in [README.md](https://github.com/xen/fontbakery/blob/master/README.md)

## Development notes

### Production Mode

Production mode has additional requirements:

* PostgreSQL, a high performance database for production systems
* [Nginx](http://nginx.org/) >=1.4.1
* [gunicorn](http://gunicorn.org/)
* [supervisor](http://supervisord.org/)

Install nginx on Ubuntu

    sudo add-apt-repository ppa:nginx/stable
    sudo apt-get update
    sudo apt-get install nginx

Make a copy of config example nginx and supervisor files in ``pwd``/webapp_configs and edit them with your server name and paths and then make symbolic link to nginx and supervisor configurations directories.

    ln -s ``pwd``/webapp_configs/nginx.conf /etc/nginx/sites-enabled/fontbakery.conf
    ln -s ``pwd``/webapp_configs/supervisor.conf /etc/supervisor/conf.d/fontbakery.conf

Make supervisor autostarted on server booting and start it, if server will be rebooted it will be started automatically:

    service supervisor start

