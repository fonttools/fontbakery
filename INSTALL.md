# How to Install Font Bakery

## Requirements 

First, install all the great libre software that Font Bakery ties together.

### Mac OS X

Install XCode and the Command Line Tools.

Install [HomeBrew](http://mxcl.github.io/homebrew/)


```sh
# Use Homebrew to install dependencies
brew install python;
# Use Homebrew's Python
echo 'export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bash_profile;
source ~/.bash_profile;
brew install sqlite libevent ttfautohint redis libmagic nodejs;
brew install fontforge --HEAD;
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
# install bower
npm install -g bower;
```

### Fedora

TODO: package ttfautohint for Fedora

```sh
# Use yum to install dependencies
sudo yum install -y python-virtualenv python sqlite sqlite-devel libevent libevent-devel fontforge redis mercurial git npm;
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
# install bower
npm install -g bower
```

### Debian & Ubuntu

```sh
# Use yum to install dependencies
sudo apt-get install -y build-essential python python-virtualenv python-pip sqlite libsqlite3-dev libevent-2.0-5 libevent-dev fontforge python-fontforge fonttools redis-server curl git mercurial nodejs libxslt1-dev libxml2-dev;
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
# install bower
npm install -g bower
```

Now your system should be ready to install Font Bakery itself!

## Installation

Font Bakery has some Python requirements, but it does not install them into your system; thanks to `virtualenv` they are installed into the `venv` directory.

```sh
mkdir ~/src;
git clone https://github.com/xen/fontbakery.git ~/src/fontbakery;
cd ~/src/fontbakery;
VENVRUN=virtualenv make setup;
cp local.example.cfg local.cfg;
open -e local.cfg;
```

Make your own `local.cfg` based on `local.example.cfg`. You can use this example:

    GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
    GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'
    SQLALCHEMY_ECHO = True

Github application info is for demo use only. Default values are for URL `http://localhost:5000/`, callback URL `http://localhost:5000/auth/callback`. 

If you run Font Bakery on a domain, you must fill in [this form](https://github.com/settings/applications/new) to make your own keys, something like this:

![Github Auth example](https://raw.github.com/xen/fontbakery/master/INSTALL-githubauth.png)

After registering your application, you will see this information:

> **Client ID**
>
>     f3076d470c4258e744a7
>
> **Client Secret**
>
>     03327cbda3271b709d0d665c6d19ee1b7a15a705

Replace these values in the local.cfg:

```
GITHUB_CONSUMER_KEY = 'f3076d470c4258e744a7'
GITHUB_CONSUMER_SECRET = '03327cbda3271b709d0d665c6d19ee1b7a15a705'
```

Update other options listed in `local.cfg`. *If you want to use
Font Bakery in production more these options are very important*.

Finally, initialise the database and run Font Bakery:

```
make init;
make run;
open 'http://localhost:5000';
```

## Production Mode 

Production mode has additional requirements:

* PostgreSQL, a high performance database for production systems
* [Nginx](http://nginx.org/) >=1.4.1
* [gunicorn](http://gunicorn.org/)
* [supervisor](http://supervisord.org/)

### Ubuntu

```
sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install nginx
```

Make a copy of config example nginx and supervisor files in `/webapp_configs` and edit them with your server name and paths

Make symbolic link to nginx and supervisor configurations directories:

```
ln -s ``pwd``/webapp_configs/nginx.conf /etc/nginx/sites-enabled/fontbakery.conf
ln -s ``pwd``/webapp_configs/supervisor.conf /etc/supervisor/conf.d/fontbakery.conf
```

Make supervisor autostarted on server booting and start it, if server will be rebooted it will be started automatically:
```
    service supervisor start
```
