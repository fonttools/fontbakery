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
brew install sqlite libevent ttfautohint redis libmagic nodejs npm;
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

```sh
# Use yum to install dependencies
sudo yum install -y python-virtualenv python sqlite sqlite-devel libevent libevent-devel fontforge redis mercurial git npm libffi-devel python-devel openssl-devel gcc ttfautohint;
# Start redis now # TODO: check this works
service redis start;
# Set up a pip download cache
echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
mkdir ~/.pip_download_cache;
# install bower
npm install -g bower
```

### Debian & Ubuntu

```sh
# Use yum to install dependencies
sudo apt-get update;
sudo apt-get install -y build-essential python python-virtualenv python-pip sqlite libsqlite3-dev libevent-2.0-5 libevent-dev fontforge python-fontforge fonttools redis-server curl git mercurial libxslt1-dev libxml2-dev automake autoconf libtool libharfbuzz-dev libharfbuzz-dev qt5-default libffi-dev ttfautohint python-software-properties g++ make libssl-dev python-dev subversion libssl-dev libffi-dev python-dev;
# for Ubuntu 12.04 you need to install nodejs via PPA since the main repo is outdated
sudo add-apt-repository ppa:chris-lea/node.js;
sudo apt-get update;
sudo apt-get install nodejs;
# Start redis now:
sudo /etc/init.d/redis-server start;
# Set up a pip download cache
echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
mkdir ~/.pip_download_cache;
# install bower
sudo npm install -g bower
```

Now your system should be ready to install Font Bakery itself!

## Installation

Font Bakery has some Python requirements, but it does not install them into your system; thanks to `virtualenv` they are installed into the `venv` directory.

```sh
# get source code
mkdir ~/src;
git clone https://github.com/googlefonts/fontbakery.git ~/src/fontbakery;
cd ~/src/fontbakery;
# install js components
cd static; bower install; cd ..;
# install py components
VENVRUN=virtualenv make setup;
# create a configuration file
cp local.example.cfg local.cfg;
```

Edit `local.cfg` with your own details. Here is an example:

> GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
> GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'
> SQLALCHEMY_ECHO = True

These Github application details are for demo use only. Default values are for URL `http://localhost:5000/`, callback URL `http://localhost:5000/auth/callback`.

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
Font Bakery in production, these options are very important*.

Finally, initialise the database and run Font Bakery:

```
make init;
make run;
```

Finally you can open <http://localhost:5000> in a modern web browser.

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
