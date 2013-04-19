# Bakery

Font bakery service project. Currently in **DEVELOPMENT MODE**.

## License

This code distibuted under Apache License, Version 2.0. 

## Installation

Requirements:

* Recent python 2.7.x version
* [GNU Make](http://www.gnu.org/software/make/), a compilation manager
* [pip](http://www.pip-installer.org), a great Python package manager
* [libevent](http://libevent.org/), a library for noticing when files are updated
* Celery server for background task processing (install automatically, but need separate running process).

Production mode requirements:

* PostgreSQL for production database

On Mac OS X you can install libevent with [Homebrew](http://mxcl.github.com/homebrew/), a great Mac OS X package manager. 

    brew install libevent

NB: Prefered way to use `python` package from brew, more information [in wiki page](https://github.com/mxcl/homebrew/wiki/Homebrew-and-Python).

You can install pip with easy_install, an older Python package manager. 

    easy_install pip

You will then need to install the `virtualenv` Python package:

    pip install virtualenv

Then you can automatically install all other requirements and compile the program:

    make

To run it on a localhost webserver, simply run,

    make run

Backery also uses celery for background task processing. So you need to run in different terminal window:

    make celery

During development process you probably need runing fake mail server for debuging, also could be run in separate terminal window:

    make mail

## Production mode 

More information about configuration available in example configuration file `local.example.cfg`. Without this file server working in development mode. 
