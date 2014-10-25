[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![Coveralls.io Test Coverage Status](https://img.shields.io/coveralls/googlefonts/fontbakery.svg)](https://coveralls.io/r/googlefonts/fontbakery)

# Font Bakery

Font Bakery is a set of command-line tools for building and testing font projects, and a web interface for reviewing them.
It runs checks on source files in UFO, SFD, OTF, TTF and TTX formats.
Then it builds them into OTF and TTF files, and runs tests on those.

If you use Github for your font project, you can use FontBakery on Travis so that with each update to your Github repository your files are built and tested, and the binary font files and test results are available on the web via Github Pages.

## Install

### Mac OS X 

Install the dependencies with [Homebrew](http://brew.sh), [PIP](http://pip.readthedocs.org) and [gem](https://rubygems.org):

```sh
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" # install homebrew
brew install python giflib libspiro; # fontforge optional dependencies
brew install --HEAD --with-x fontforge; # fontforge
brew install ttfautohint swig; # fontbakery dependencies 
easy_install pip # install pip
pip install git+https://github.com/behdad/fontTools.git; # fontbakery dependencies 
pip install git+https://github.com/googlefonts/fontcrunch.git; # fontbakery dependencies 
sudo gem install travis; # fontbakery dependencies 
pip install git+https://github.com/googlefonts/fontbakery.git; # install fontbakery
```

### GNU+Linux

```sh
sudo add-apt-repository --yes ppa:fontforge/fontforge;
sudo apt-get update -qq;
sudo apt-get install python-fontforge ttfautohint swig;
pip install git+https://github.com/behdad/fontTools.git;
pip install git+https://github.com/googlefonts/fontcrunch.git;
pip install git+https://github.com/googlefonts/fontbakery.git;
```

## Usage

### On Your Computer

All fontbakery commands begin with `fontbakery-`

### On Travis

[Travis-CI.org](http://travis-ci.org) is a Continuous Integration system that will run Font Bakery on your files each time you update them on Github.
After building your fonts, it will publish the build to the `gh-pages` branch of your repository.

**Warning:** This will replace the entire contents of the `gh-pages` branch if any exist. The previous versions will be available in git history, though.

Travis requires a `.travis.yml` file in the root directory of your repository. 
Full documentation is available from [docs.travis-ci.com](http://docs.travis-ci.com/) but you can use a typical template.

1. Enable your font repository in your travis profile, [travis-ci.org/profile](https://travis-ci.org/profile)

2. Create the `.travis.yml` text file with your favorite text editor as follows:
   
   ```yml
   language: python
   before_install:
   - sudo add-apt-repository --yes ppa:fontforge/fontforge
   - sudo apt-get update -qq
   - sudo apt-get install python-fontforge ttfautohint swig
   - cp /usr/lib/python2.7/dist-packages/fontforge.* "$HOME/virtualenv/python2.7.8/lib/python2.7/site-packages"
   install:
   - pip install git+https://github.com/behdad/fontTools.git
   - pip install git+https://github.com/googlefonts/fontcrunch.git
   - pip install git+https://github.com/googlefonts/fontbakery.git
   before_script:
   - mkdir -p builds/$TRAVIS_COMMIT
   script: (set -o pipefail; PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-build.py . 2>&1 | tee -a    builds/$TRAVIS_COMMIT/buildlog.txt)
   after_script:
   - PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-report.py builds/$TRAVIS_COMMIT
   - rm -rf builds/$TRAVIS_COMMIT/sources
   - rm -rf builds/$TRAVIS_COMMIT/build.state.yaml
   - PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-travis-deploy.py
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
