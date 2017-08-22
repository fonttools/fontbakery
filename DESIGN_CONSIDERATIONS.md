### Usage On Travis

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
