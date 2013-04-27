# Bakery

Font bakery service project. Currently in **DEVELOPMENT MODE**.

## License

This code distributed under the Apache License, Version 2.0.

See [LICENSE.txt](LICENSE.txt) for full details.

## Installation

Install should be easy, and work on Mac OS X if you have XCode's Command Line Tools installed.

(If you have any problems installing, please file an issue and I will provide additional instructions.)

### Requirements

* Mac OS X: XCode + Command Line Tools
* Python 2.7
* [GNU Make](http://www.gnu.org/software/make/), a compilation manager
* [pip](http://www.pip-installer.org), a great Python package manager
* [libevent](http://libevent.org), a library for noticing when files are updated
* [Celery](http://celeryproject.org), a server for background task processing (installed automatically, but runs as a separate process.)

### Instructions

On Mac OS X you can install libevent with [Homebrew](http://mxcl.github.com/homebrew/), a great Mac OS X package manager:

    brew install libevent

Suggestion: Use the [Homebrew `python` package](https://github.com/mxcl/homebrew/wiki/Homebrew-and-Python).

You can install `pip` with `easy_install`, an older Python package manager:

    easy_install pip

You will then need to install the `virtualenv` Python package:

    pip install virtualenv

Now you can begin to install Bakery. 

    git clone https://github.com/xen/bakery.git bakery;
    cd bakery

Then you can automatically install all other requirements and compile the program:

    make setup

This will take some time. I have removed versions info so now its takes longer time to install, but is more thorough. 

TODO: Explain here how to use the local python eggs cache to speed up this process

Now copy the example configuration file `local.example.cfg` to `local.cfg` and edit it:

    cp local.example.cfg local.cfg

TODO: Explain here how to create a local.cfg

Init database tables:

    make init

To run it on a localhost webserver, simply run,

    make run

Open http://localhost:5000/ in your browser

During development process you probably need to be running a fake mail server,

    make mail

## Development notes

### Login failing?

Sometimes it is possible that some cookies stay in a browser from old runs, or even different applications, since localhost is commonly used in web development. If you try to login but fail, then visit http://localhost:5000/auth/logout and try to log in again.

### Production Mode 

More information about configuration available in example configuration file `local.example.cfg`. Without this file, Bakery runs in development mode. 

Production mode has additional requirements:

* PostgreSQL, a high performance database for production systems

TODO: Is this section correct?
