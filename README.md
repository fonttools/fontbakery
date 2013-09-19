# Font Bakery

Font Bakery is a font build service. The vision is to bring the [Continuous Integration](http://en.wikipedia.org/wiki/Continuous_integration) best practices of software development to [type design](http://en.wikipedia.org/wiki/Type_design).

You give it a font project git repository, tell it which license the project is under, which font source files you wish to build into binaries, and set some build options. It then runs tests on the sources, and if they pass, builds the fonts and runs further tests on the binaries.

This project is under active development by Mikhail Kashkin and Dave Crossland.

## Disclaimer

This project was given financial support by Google Fonts team within Google, Inc. The copyright to contributions done with that financial support is owned by Google, Inc. but Font Bakery is not an official Google product.

## Installation

The installation process is easy, and full instructions are maintained in the [INSTALL](./INSTALL.md) file.

## Usage

After installation, this command will update the dashboard stats:

    $ make stats;

This command will start the worker:

    $ make worker;

Then this command will start the web service on a localhost web server:

    $ make run;

Then open http://localhost:5000 in your browser. You will be warned if the worker is not running.

You may with to clear out all user data:

    $ make clean;

During the development process you may wish to be run a fake mail server:

    $ make mail;

## Development

A 1 hour video (recorded on 2013-09-02) explaining the basic functionality and overall codebase is here: https://www.youtube.com/watch?v=paKa_Kok2EA

#### License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

This software has many dependencies under other, compatible, licenses.
