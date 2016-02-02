[![Latest PyPI Version](https://img.shields.io/pypi/v/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Python](https://img.shields.io/pypi/pyversions/fontbakery.svg?style=flat)](https://pypi.python.org/pypi/fontbakery/)
[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![Coveralls.io Test Coverage Status](https://img.shields.io/coveralls/googlefonts/fontbakery.svg)](https://coveralls.io/r/googlefonts/fontbakery)

# Font Bakery

Font Bakery is a set of command-line tools for building and testing font projects, and a web interface for reviewing them.
It runs checks on source files in UFO, SFD or TTX formats and via FontForge or AFDKO builds them into OTF and TTF files (plus the files needed for hosting in Google Fonts.)
It runs tests on the build results, and the test logs can be parsed into graphical views by the Font Bakery web app.

Optionally, if you are developing a font project publicly with Github or a similar host, you can set up a Continuous Integration server like Travis to run FontBakery on each commit, so that with each update your files are built and tested in the CI server and then uploaded to the project's `gh-pages` branch for browsing and testing live.

Font Bakery is not an official Google project, and Google provides no support for it.

Font Bakery has been presented at the following events:

* 2014-04-03: Libre Graphics Meeting 2014 [slides](https://speakerdeck.com/davelab6/lgm-2014-font-bakery)

## Install

### Mac OS X

Install the dependencies with [Homebrew](http://brew.sh), [PIP](http://pip.readthedocs.org) and [gem](https://rubygems.org):

```sh
xcode-select --install;
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" # install homebrew
brew install python giflib libspiro; # fontforge optional dependencies
brew install fontforge --with-extra-tools --HEAD ; # fontforge
brew install libmagic ttfautohint swig; # fontbakery dependencies
easy_install pip # install pip
pip install virtualenv; # optional, can be useful
pip install git+https://github.com/behdad/fontTools.git; # fontbakery dependency
pip install git+https://github.com/googlefonts/fontcrunch.git; # fontbakery dependency
pip install git+https://github.com/davelab6/pyfontaine.git; # fontbakery dependency
sudo gem install travis; # fontbakery dependencies
sudo pip install git+https://github.com/googlefonts/fontbakery.git; # install fontbakery as root to ensure it uses system python
```

### GNU+Linux

```sh
sudo add-apt-repository --yes ppa:fontforge/fontforge;
sudo apt-get update -qq;
sudo apt-get install python-fontforge ttfautohint swig libicu-dev;
sudo pip install pyicu;
pip install git+https://github.com/behdad/fontTools.git;
pip install git+https://github.com/googlefonts/fontcrunch.git;
pip install git+https://github.com/googlefonts/fontbakery.git;
```

## Usage

### On Your Computer

All fontbakery commands begin with `fontbakery-`

You will have a font project directory with your source files.
The first step is to add a `bakery.yml` file that contains settings for Font Bakery to follow.
An interactive terminal application will create one in its current directory:

    cd ~/src/github.com/davelab6/fontproject/;
    fontbakery-setup.py;

You can then run the build process with this file.
It is helpful to run in verbose mode.


    fontbakery-build.py --verbose bakery.yaml;

This will run many individual fontbakery tools, such as

* `fontbakery-check.py` to check a font file
* `fontbakery-build-font2ttf.py` to convert a ufo or otf to a ttf with fontforge
* `fontbakery-build-metadata.py` to create a METADATA.pb file

The check tool will fix some problems, and you can run these fixing tools individually also:

* `fontbakery-fix-ascii-fontmetadata.py`
* `fontbakery-fix-dsig.py`
* `fontbakery-fix-fstype.py`
* `fontbakery-fix-gasp.py`
* `fontbakery-fix-glyph-private-encoding.py`
* `fontbakery-fix-nbsp.py`
* `fontbakery-fix-opentype-names.py`
* `fontbakery-fix-style-names.py`
* `fontbakery-fix-vertical-metrics.py`

#### Other tools

There are some fontbakery tools not used in the build process:

* `fontbakery-report.py` builds reports
* `fontbakery-travis-deploy.py` and `fontbakery-travis-secure.sh` are used to set up a `.travis.yml` file (see below)

`fontbakery-metadata-vs-api.py` will compare families with a METADATA.pb file with those in the production Google Fonts API.
The output is very long, so its helpful to pipe the output and errors to files:

    fontbakery-metadata-vs-api.py --api=fonts.googleapis.com \
      --cache=/tmp/fontbakery-compare-github-api --verbose \
      GoogleFontsDeveloperAPIKey /Users/username/fonts \
      > fontbakery-metadata-vs-api-stdout.txt \
      2> fontbakery-metadata-vs-api-stderr.txt ;

### On Travis

[Travis-CI.org](http://travis-ci.org) is a Continuous Integration system that will run Font Bakery on your files each time you update them on Github.
After building your fonts, it will publish the build to the `gh-pages` branch of your repository.

**Warning:** This will replace the entire contents of the `gh-pages` branch if any exist.
The previous versions will be available in git history, though.

Travis requires a `.travis.yml` file in the root directory of your repository.
Full documentation is available from [docs.travis-ci.com](http://docs.travis-ci.com/) but you can use a typical template.

Steps below can be ignored if you use `fontbakery-travis-init.py` script. It gets path to repo as an argument and make all steps to update your .travis.yml with token from github. Optional arguments are `-u, --user` and `-e, --email`. Script will ask you for all info if something missed. Actually it is enough to set user name and email inside .git/config. Last actions script will do for you.

1. Enable your font repository in your travis profile, [travis-ci.org/profile](https://travis-ci.org/profile)

2. Create the `.travis.yml` text file with your favorite text editor as follows:

   ```yml
   language: python
   before_install:
   - sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
   - sudo add-apt-repository --yes ppa:fontforge/fontforge
   - sudo apt-get update -qq
   - sudo apt-get install python-fontforge ttfautohint swig libicu-dev
   - cp /usr/lib/python2.7/dist-packages/fontforge.* "$HOME/virtualenv/python2.7.9/lib/python2.7/site-packages"
   # See issue travis-ci/travis-ci#1379
   - sudo apt-get install -qq g++-4.8
   - export CXX="g++-4.8" CC="gcc-4.8"
   - git clone https://github.com/khaledhosny/ots
   - cd ots
   - ./autogen.sh
   - ./configure
   - make
   - sudo make install
   - cd ..
   install:
   - pip install pyicu
   - pip install git+https://github.com/behdad/fontTools.git
   - pip install git+https://github.com/googlefonts/fontcrunch.git
   - pip install git+https://github.com/googlefonts/fontbakery.git
   before_script:
   - mkdir -p builds/$TRAVIS_COMMIT
   script: (set -o pipefail; PATH=/home/travis/virtualenv/python2.7.9/bin/:$PATH fontbakery-build.py . 2>&1 | tee -a    builds/$TRAVIS_COMMIT/buildlog.txt)
   after_script:
   - PATH=/home/travis/virtualenv/python2.7.9/bin/:$PATH fontbakery-report.py builds/$TRAVIS_COMMIT
   - rm -rf builds/$TRAVIS_COMMIT/sources
   - rm -rf builds/$TRAVIS_COMMIT/build.state.yaml
   - PATH=/home/travis/virtualenv/python2.7.9/bin/:$PATH fontbakery-travis-deploy.py
   branches:
     only:
     - master
   ```

3. Add the `secure` section to the file.
   First fetch a Github secure token for your repository, replacing `yourGithubUsername` and `yourRepoName` with your own:
   ```sh
   curl -u yourGithubUsername \
       -d '{"scopes":["public_repo"],"note":"FontBakery for yourRepoName"}' \
       -s "https://api.github.com/authorizations";
   ```

  If you use 2-Factor Authentication, use the following:
  ```sh
  curl -i -u yourGithubUsername -H "X-GitHub-OTP: optCode" \
    -d '{"scopes": ["public_repo"], "note": "FontBakery for yourRepoName"}' \
    https://api.github.com/authorizations
  ```

  If you get the following response, you already have a token for `note`, and you can find it on your [github profile page](https://github.com/settings/applications#personal-access-tokens)
   ```json
   {
     "message": "Validation Failed",
     "documentation_url": "https://developer.github.com/v3/oauth_authorizations/#create-a-new-authorization",
     "errors": [
       {
         "resource": "OauthAccess",
         "code": "already_exists",
         "field": "description"
       }
     ]
   }
   ```

  For the next step you'll need to have the travis command-line utility installed.
  It can be installed with the following commands:

  ```sh
  sudo apt-get install ruby1.9.1-dev
  sudo gem install travis -v 1.8.0 --no-rdoc --no-ri
  ```

  Now add the token using the travis command, replacing `yourGithubUserEmail` and `yourGithubRepoToken` with your own:
  ```sh
  travis encrypt GIT_NAME="yourGithubUsername" \
    GIT_EMAIL="yourGithubUserEmail" \
    GH_TOKEN="yourGithubRepoToken" \
    --add --no-interactive -x;
  ```

4. Add and commit your `.travis.yml` file and push it to Github.
   ```sh
   git add .travis.yml;
   git commit .travis.yml -m "Adding .travis.yml";
   git push origin master;
   ```

5. After each build by Travis you can see a report at <http://yourGithubUsername.github.io/yourRepo>

### `bakery.yaml` files

These files control the bake process. 

Create them with the setup tool, eg `fontbakery-setup.py .`

* `notes` can store notes on the build, and are shown in the web ui.
