# This would be so much easier if the Open Bakery repo had kept the full git history...
# So here we have to curate a set of patches to automate keeping the projects
# in sync except for the extremely rare occasions when there's disagreement on what
# Miguel Sousa is doing there.

# Backup our changelog:
mv CHANGELOG.md CHANGELOG.md.fontbakery

#### Get the latest contents from the Open Bakery github repo ####
cd ~/devel/openbakery/
git fetch origin
git rebase origin/main
cd ~/fb

cp ~/devel/openbakery/* . -rf  # Start by over-writting everything
                               # on our clean FontBakery git repo.

# Also copy the dot dirs (such as .github/workflows)
mv .git .git_backup
cp ~/devel/openbakery/.[^.]* . -rf
rm -rf .git
mv .git_backup .git

cp Lib/openbakery/* -rf Lib/fontbakery/  # But the directory has the fork's name, so we
rm -rf Lib/openbakery                    # move its contents and delete the directory


# also rename this file, so that we can see whether there were updates on the Miguel's repo:
mv Lib/fontbakery/data/openbakery-microsoft-vendorlist.cache Lib/fontbakery/data/fontbakery-microsoft-vendorlist.cache

# preserve correct API names
# (These are subtle case-name differences. We may want to address these quirks of the API on a major release in the future):
git grep -rl OpenBakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/OpenBakeryCallable/FontbakeryCallable/g'
git grep -rl OpenBakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/OpenBakeryReporter/FontbakeryReporter/g'
git grep -rl OpenBakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/OpenBakeryError/FontbakeryError/g'

# auto-replace github URLs:
git grep -rl openbakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/miguelsousa\/openbakery/googlefonts\/fontbakery/g'

# auto-replace project name:
git grep -rl openbakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/openbakery/fontbakery/g'
git grep -rl OpenBakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/OpenBakery/FontBakery/g'

# Instances of abusive, harassing, or otherwise unacceptable behavior may be
# reported to the community leaders responsible for enforcement at:
sed -i 's/miguel.sousa@adobe.com/dcrossland@google.com/g' CODE_OF_CONDUCT.md

# If you have any questions or concerns regarding these guidelines or the Project,
# please contact...
sed -i 's/Miguel Sousa at miguel.sousa@adobe.com./us via the issue tracker or send an email to Felipe Sanches at juca@members.fsf.org/g' CONTRIBUTING.md

##### Now here's the patching out of the things we don't need: #####

# We do not need the fork's logo:
rm -f data/openbakery.jpg

# We have our own changelog:
mv CHANGELOG.md.fontbakery CHANGELOG.md

# We also have our own documentation for now,
# even though I would be happy to merge both projects docs soon:
rm .github/workflows/docs.yml
rm docs/Gemfile
rm docs/Gemfile.lock
rm docs/_config.yml
rm docs/developer-guide.md
rm docs/index.md
rm docs/user-guide.md

# These are OpenBakery branding & URLs:
# patch -p1 -R < openbakery_backporting/patches/0001-OpenBakery-branding-URLs.patch

# We still use the sphinx dependency for building the Font Bakery Read The Docs pages.
# We also use the header line
# --index-url https://pypi.python.org/simple/
# following advice from Cosimo Lupo, for the reasons described at the article at:
# https://caremad.io/posts/2013/07/setup-vs-requirement/
# More detailed info at: https://github.com/googlefonts/fontbakery/issues/2174
patch -p1 -R < openbakery_backporting/patches/0002-requirements-tests.txt.patch

# I don't want to delete the comment stating that the munkres dependency
# should actually be a fonttools dependency
patch -p1 -R < openbakery_backporting/patches/0003-requirements.txt.patch

# Renovate sounds like a good tool, but I am not ready yet to deploy it
# on the GoogleFonts github org. I would have to ask some team members first.
rm renovate.json

# Codecov also looks great, but I am a bit weary of giving it GitHub authorization
# to "Act on my behalf". I need a bit more time to think about it.
rm codecov.yml
patch -p1 -R < openbakery_backporting/patches/0004-Codecov-also-looks-great-but.patch


##### A few tweaks to the CONTRIBUTING.md file: #####
# These URLs are broken:
#   https://miguelsousa.github.io/fontbakery/dev-setup.html
#   https://miguelsousa.github.io/fontbakery/run-tests-locally.html
#
# Projects hosted at the googlefonts github organization need a CLA signature.
# Note: We may in the future migrate FontBakery away from the googlefonts github org
#       in order to more clearly signal that it is not a Google-biased project.
#
# We also improved the description of the project goals.



##### FontBakery's fixes that should be applied to Open Bakery as well:

# Fix for setuptools-scm, overwise package version always ends up being "0.1.dev1":
patch -p1 -R < openbakery_backporting/patches/0005-unshallow-fetch-for-setuptools-scm-otherwise-the-ver.patch

