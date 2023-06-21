# This would be so much easier if the Open Bakery repo had kept the full git history...
# So here we have to curate a set of patches to automate keeping the projects
# in sync except for the extremely rare occasions when there's disagreement on what
# Miguel Sousa is doing there.

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


# auto-replace project name:
git grep -rl openbakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/openbakery/fontbakery/g'
git grep -rl OpenBakery -- ':(exclude)openbakery_backporting/' | xargs sed -i 's/OpenBakery/FontBakery/g'


##### Now here's the patching out of the things we don't need: #####

rm -f data/openbakery.jpg  # We do not need the fork's logo

# We still use the sphinx dependency for building the Font Bakery Read The Docs pages.
# We also use the header line
# --index-url https://pypi.python.org/simple/
# following advice from Cosimo Lupo, for the reasons described at the article at:
# https://caremad.io/posts/2013/07/setup-vs-requirement/
# More detailed info at: https://github.com/googlefonts/fontbakery/issues/2174
patch -p1 -R < openbakery_backporting/patches/requirements-tests.txt.patch

# I don't want to delete the comment stating that the munkres dependency
# should actually be a fonttools dependency
patch -p1 -R < openbakery_backporting/patches/requirements.txt.patch

# Renovate sounds like a good tool, but I am not ready yet to deploy it
# on the GoogleFonts github org. I would have to ask some team members first.
rm renovate.json

# Codecov also looks great, but I am a bit weary of giving it GitHub authorization
# to "Act on my behalf". I need a bit more time to think about it.
rm codecov.yml
rm .coveragerc


