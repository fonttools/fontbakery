bakery
======

Font bakery service. 

License
--------

[GNU General Public License v3.0, or later](http://www.gnu.org/licenses/gpl)

Installation
--------------

Requirements:

* Recent python 2.7.x version
* [GNU Make](http://www.gnu.org/software/make/), a compilation manager
* [pip](http://www.pip-installer.org), a great Python package manager
* [libevent](http://libevent.org/), a library for noticing when files are updated

On Mac OS X you can install libevent with [Homebrew](http://mxcl.github.com/homebrew/), a great Mac OS X package manager. 

    brew install libevent

You can install pip with easy_install, an older Python package manager. 

    easy_install pip

You will then need to install the `virtualenv` Python package:

    pip install virtualenv

Then you can automatically install all other requirements and compile the program:

    make

To run it on a localhost webserver, simply run,

    make run