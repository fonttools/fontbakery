[![Travis Build Status](https://travis-ci.org/googlefonts/fontbakery.svg)](https://travis-ci.org/googlefonts/fontbakery)
[![Coveralls.io Test Coverage Status](https://img.shields.io/coveralls/googlefonts/fontbakery.svg)](https://coveralls.io/r/googlefonts/fontbakery)

# FontBakery CLI

FontBakery CLI can build UFO, SFD, or TTX font projects. You can set it up
with Travis and Github Pages so that each update to your Github repo is built
and tested, and the binary font files and test results are available on the web.

Easy way to start with fontbakery is to configure it with travis that will test
and autofix your fonts and publish to gh-pages branch of your repository or will
send or send result baked fonts even to your email.


## Minimal configuration (`.travis.yml`)

Detailed description of .travis.yml configuration you can read by following
to [travis documentation](http://docs.travis-ci.com/).

1. Enable your font repository in [your travis profile](https://travis-ci.org/profile/)

2. Create with your favorite editor `.travis.yml`

3. Place there minimal required configuration to `.travis.yml`:

```
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
script: (set -o pipefail; PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-build.py . 2>&1 | tee -a builds/$TRAVIS_COMMIT/buildlog.txt)
branches:
  only:
  - master
```

4. Before you push it to your github repo you need add `secure` section.

a. `$ sudo gem install travis  # first install travis`

b. `$ curl -u <githubUserName> -d '{"scopes":["public_repo"],"note":"<note>"}' -s "https://api.github.com/authorizations"  # <note> and <githubUserName> must be replaced with your own`

Sometimes you can receive this response from github:

```
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

This means that you already have token for <note>. If you do not remember you
can refresh token on your [github profile page](https://github.com/settings/applications#personal-access-tokens).

c. `travis encrypt GIT_NAME="<githubUserName>" GIT_EMAIL="<githubUserEmail>" GH_TOKEN="<token>" --add --no-interactive -x`

Now you can push it to repo and enjoy with fontbakery build process


### Extending `.travis.yml` to read reports

You can use fontbakery report application to visualize font tests and to
fix them.

1. Change `.travis.yml` by adding `after_script` section

```
after_script:
- PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-report.py builds/$TRAVIS_COMMIT
- rm -rf builds/$TRAVIS_COMMIT/sources
- rm -rf builds/$TRAVIS_COMMIT/build.state.yaml
- PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-travis-deploy.py
```

2. Push it

Travis will build your font and then will deploy it to `gh-pages` branch. Be aware!
Deploying override your actual files in `gh-pages` branch!

After you success to build your font and deploy, you can see report at the
<username>.github.io/<reponame>.
