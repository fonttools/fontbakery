# Bakery

Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then builds these fonts and runs tests on both sources and binaries.

This project is under active development by Mikhail Kashkin and Dave Crossland. 

## License

This code distributed under the Apache License, Version 2.0.

See [LICENSE.txt](LICENSE.txt) for full details.

## Installation

Install should be easy, and work on Mac OS X if you have XCode's Command Line Tools installed.

Full instructions in [INSTALL.md](./INSTALL.md) file.

### Instructions

When you have installed environment run local webserver:

    $ make run

Open http://localhost:5000/ in your browser

During development process you probably need to be running a fake mail server,

    make mail
