# Installation instructions

This documents is step by step instruction how to setup development and poduction environment. As long as project in development stage production part subject to change. 

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

If you use Mac OS X, a convenient way to install such UNIX software is use [HomeBrew](http://mxcl.github.io/homebrew/). 

Install HomeBrew and then run these commands in the Terminal:

```sh
    brew install python sqlite libevent fontforge ttfautohint redis
    # To have launchd start redis at login:
    ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents
    # Then to load redis now:
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist
```

Then install the python dependencies for setting up the project's own python packages:

```sh
    which easy_install-2.7 
    # /usr/local/share/python/easy_install-2.7
    sudo easy_install-2.7 -U pip;
    sudo easy_install-2.7 -U virtualenv;
    echo export PIP_DOWNLOAD_CACHE=$HOME/.pip_download_cache >>~/.profile;
    mkdir ~/.pip_download_cache;
```

Now your system should be ready.

## Installation

Install your local environment is very easy. Project require some system programms installed, but do not install its own dependencies into system. All packages installs into folder `venv`.

Clone Google Font Directory Mercurial Repository from Google Code into new folder:

    hg clone https://code.google.com/p/googlefontdirectory/ 

Clone code from github into new folder:

    git clone https://github.com/xen/fontbakery.git fontbakery

Copy the Google Font Directory lint.jar tool into the fontbakery/scripts directory:

    cp -pa ~/googlefontdirectory/tools/lint/dist/lint.jar scripts/

Then run setup:

    cd fontbakery
    make setup

Wait some time.

NB: As `fontforge` cann't be installed using pip and is installed into your system python's site packaged make sure that 
default python interpreter (`which python`) is the same where you installed `fontforge` and other dependencies. 

**Optional step**: Make your own `local.cfg` based on `local.example.cfg`. Or use this as example:

    GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
    GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'
    SQLALCHEMY_ECHO = True

Github application info is for demo use only. You can [make your own](https://github.com/settings/applications/new). Default values for URL `http://localhost:5000/`, callback URL `http://localhost:5000/auth/callback`. 

Init database tables:

    make init

And run project:

    make run

Run tasks daemon worker in different console

    make worker

Open [http://localhost:5000/](http://localhost:5000/) in your browser

## Development notes

### Login failing?

Sometimes it is possible that some cookies stay in a browser from old runs, or even different applications, since localhost is commonly used in web development. If you try to login but fail, then visit [http://localhost:5000/auth/logout](http://localhost:5000/auth/logout) and try to log in again.

### Production Mode 

Production mode has additional requirements:

* PostgreSQL, a high performance database for production systems

By default project will start in development mode, but it is possible to run in production making changes in `local.cfg`. More instructions will follow.

