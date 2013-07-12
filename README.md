# Bakery

Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then builds these fonts and runs tests on both sources and binaries.

This project is under active development by Mikhail Kashkin and Dave Crossland. 

## License

This software is distributed under the [Apache License, Version 2.0](LICENSE.txt), and has many dependencies under compatible licenses.

## Installation

The installation process is easy, and full instructions are maintained in the [INSTALL](./INSTALL.md) file.

## Instructions

After installation, this command will start the service on a localhost web server:

    $ make run

Then open http://localhost:5000 in your browser

During the development process you will need to be running a fake mail server,

    $ make mail
