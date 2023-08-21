# NOTE: As of July 18, 2023, I finally have been able to finish inspecting the full set
#       of changes in OpenBakery and documented them below.
#
#       Using as a reference, code from the following commit:
#       https://github.com/miguelsousa/openbakery/commit/0b29c2db3b4f076c9e651eb8f97281a40d216a0c
#
#
# This task would be so much easier if the Open Bakery repo had kept the full git history...
# So here we have to curate a set of patches to automate keeping the projects
# in sync except for the extremely rare occasions when there's disagreement on what
# Miguel Sousa is doing there.


# Backup a few things:
rm -rf ../fontbakery-tmp-backup
mkdir ../fontbakery-tmp-backup
mv data/logo.png ../fontbakery-tmp-backup/
mv data/logo.svg ../fontbakery-tmp-backup/
mv CHANGELOG.md ../fontbakery-tmp-backup/
mv README.md ../fontbakery-tmp-backup/
mv venv ../fontbakery-tmp-backup
mv .git ../fontbakery-tmp-backup
mv docs ../fontbakery-tmp-backup/
mv Lib/fontbakery/sphinx_extensions/ ../fontbakery-tmp-backup/
mv openbakery ../fontbakery-tmp-backup/

# Also keeping these things that I still do not understand why Miguel deleted:
mv snippets/ ../fontbakery-tmp-backup/
mv MANIFEST.in ../fontbakery-tmp-backup/
mv .readthedocs.yml ../fontbakery-tmp-backup/
mv .pre-commit-config.yaml ../fontbakery-tmp-backup/
mv .editorconfig ../fontbakery-tmp-backup/
mv data/test/README.txt ../fontbakery-tmp-backup/data-test-README.txt

#### Get the latest contents from the Open Bakery github repo ####
cd ~/devel/openbakery/
git fetch origin
git rebase origin/main
cd ~/fb

# Start by over-writting everything on our clean FontBakery git repo.
rsync --inplace -av --delete-excluded ~/devel/openbakery/ .

# Restore our .git
rm -rf .git
mv ../fontbakery-tmp-backup/.git .

# But the directory has the fork's name, so we move its contents and delete the directory
mkdir Lib/fontbakery/
cp Lib/openbakery/* -rf Lib/fontbakery/
rm -rf Lib/openbakery

# Also rename this file, so that we can see whether there were updates on the Miguel's repo:
mv Lib/fontbakery/data/openbakery-microsoft-vendorlist.cache Lib/fontbakery/data/fontbakery-microsoft-vendorlist.cache

# Bring back the patching & syncing directory ;-)
mv ../fontbakery-tmp-backup/openbakery .

# Preserve correct API names
# (These are subtle case-name differences. We may want to address these quirks of the API on a major release in the future):
git grep -rl OpenBakery -- ':(exclude)openbakery/' | xargs sed -i 's/OpenBakeryCallable/FontbakeryCallable/g'
git grep -rl OpenBakery -- ':(exclude)openbakery/' | xargs sed -i 's/OpenBakeryReporter/FontbakeryReporter/g'
git grep -rl OpenBakery -- ':(exclude)openbakery/' | xargs sed -i 's/OpenBakeryError/FontbakeryError/g'

# auto-replace github URLs:
git grep -rl openbakery -- ':(exclude)openbakery/' | xargs sed -i 's/miguelsousa\/openbakery/googlefonts\/fontbakery/g'

# "An OpenBakery report" => "A FontBakery report"
git grep -rl openbakery -- ':(exclude)openbakery/' | xargs sed -i 's/An OpenBakery/A FontBakery/g'

# auto-replace project name:
git grep -rl openbakery -- ':(exclude)openbakery/' | xargs sed -i 's/openbakery/fontbakery/g'
git grep -rl OpenBakery -- ':(exclude)openbakery/' | xargs sed -i 's/OpenBakery/FontBakery/g'


# fix author_email field on setup.py:
sed -i 's/miguel.sousa@adobe.com/juca@members.fsf.org/g' setup.py

# Instances of abusive, harassing, or otherwise unacceptable behavior may be
# reported to the community leaders responsible for enforcement at:
sed -i 's/miguel.sousa@adobe.com/dcrossland@google.com/g' CODE_OF_CONDUCT.md

# If you have any questions or concerns regarding these guidelines or the Project,
# please contact...
sed -i 's/Miguel Sousa at miguel.sousa@adobe.com./us via the issue tracker or send an email to Felipe Sanches at juca@members.fsf.org/g' CONTRIBUTING.md

##### Now here's the patching out of the things we don't need: #####

# We do not need the fork's logo:
rm -f data/openbakery.jpg

# And we keep ours:
mv ../fontbakery-tmp-backup/logo.png data
mv ../fontbakery-tmp-backup/logo.svg data

# We have our own changelog and readme:
mv ../fontbakery-tmp-backup/CHANGELOG.md .
mv ../fontbakery-tmp-backup/README.md .

# And our own virtual environment
rm -rf venv
mv ../fontbakery-tmp-backup/venv .

# And restore those things deleted by Miguel that I still have to look more carefully (TODO):
mv ../fontbakery-tmp-backup/snippets/ .
mv ../fontbakery-tmp-backup/MANIFEST.in .
mv ../fontbakery-tmp-backup/.pre-commit-config.yaml .
mv ../fontbakery-tmp-backup/.editorconfig .

# We also have our own documentation for now,
# even though I would be happy to merge both projects docs soon:
rm .github/workflows/docs.yml
rm docs/Gemfile
rm docs/Gemfile.lock
rm docs/_config.yml
rm docs/developer-guide.md
rm docs/index.md
rm docs/user-guide.md
mv ../fontbakery-tmp-backup/docs .
mv ../fontbakery-tmp-backup/.readthedocs.yml .
mv ../fontbakery-tmp-backup/sphinx_extensions ./Lib/fontbakery/


echo "\n=============="
echo "The data/test/README.txt has important guidelines on how the test files should"
echo " be taken care of to ensure code-tests are not broken by edits to those files."
mv ../fontbakery-tmp-backup/data-test-README.txt ./data/test/README.txt

echo "\n=============="
echo "We still use the sphinx dependency for building the Font Bakery Read The Docs pages."
echo "We also use the header line"
echo " --index-url https://pypi.python.org/simple/"
echo " following advice from Cosimo Lupo, for the reasons described at the article at:"
echo " https://caremad.io/posts/2013/07/setup-vs-requirement/"
echo " More detailed info at: https://github.com/fonttools/fontbakery/issues/2174"
echo ""
patch -p1 -R < openbakery/patches/0002-requirements-tests.txt.patch

echo "\n=============="
echo "I don't want to delete the comment stating that the munkres dependency"
echo " should actually be a fonttools dependency"
echo ""
patch -p1 -R < openbakery/patches/0003-requirements.txt.patch

echo "\n=============="
echo "Renovate sounds like a good tool, but I am not ready yet to deploy it"
echo " on the GoogleFonts github org. I would have to ask some team members first."
echo ""
rm renovate.json

echo "\n=============="
echo "Codecov also looks great, but I am a bit weary of giving it GitHub authorization"
echo "to 'Act on my behalf'. I need a bit more time to think about it."
echo ""
rm codecov.yml
patch -p1 -R < openbakery/patches/0004-Codecov-also-looks-great-but.patch

echo "\n\n##### A few tweaks to the CONTRIBUTING.md file: #####\n"
echo "\n=============="
echo "These URLs are broken:"
echo "  https://miguelsousa.github.io/fontbakery/dev-setup.html"
echo "  https://miguelsousa.github.io/fontbakery/run-tests-locally.html"
echo ""
echo "Projects hosted at the googlefonts github organization need a CLA signature."
echo "Note: We may in the future migrate FontBakery away from the googlefonts github org"
echo "      in order to more clearly signal that it is not a Google-biased project."
echo ""
echo "We also improved the description of the project goals."
echo ""
patch -p1 -R < openbakery/patches/0005-fixes-to-CONTRIBUTING.md.patch


echo "\n\n##### FontBakery's fixes that should be applied to Open Bakery as well: #####\n"

echo "\n=============="
echo "Fix for setuptools-scm, overwise package version always ends up being '0.1.dev1'"
echo ""
patch -p1 -R < openbakery/patches/0006-unshallow-fetch-for-setuptools-scm-otherwise-the-ver.patch

echo "\n=============="
echo "Font Bakery won't remove the 'check-' prefix from commands like 'check-googlefonts'"
echo " or 'check-universal' on the command line because there may be other commands in"
echo " the future such as 'fix-something' as we had in the past."
echo ""
echo "Those fixers were split out into the gftools project, but may be reintroduced"
echo " later. It is good to keep the prefix, which has a purpose equivalent"
echo " to a 'namespace'."
echo ""
echo "This was discussed at:"
echo "https://github.com/miguelsousa/openbakery/commit/489a2cc76e009a7c7a6d4bd3d4f3be1a9db641bd#commitcomment-119393361"
echo ""
patch -p1 -R < openbakery/patches/0007-Removal-of-check-prefix-on-subcommands.patch


echo "\n=============="
echo "FontBakery won't change FontValidator ERROR into a FAIL."
echo ""
echo " - A FAIL is a problem in a font."
echo " - An ERROR is a bug in the program or a bad setup, such as a missing third-party tool in the system."
echo ""
echo "When FontValidator is not installed, it is treated as a bad system setup, thus,"
echo " it is classified as an ERROR. It is not a FAIL because it is not a font problem."
echo ""
echo "This was discussed at:"
echo "https://github.com/miguelsousa/openbakery/issues/30#issuecomment-1600765260"
echo ""
patch -p1 -R < openbakery/patches/0009-FontBakery-won-t-change-FontValidator-ERROR-into-a-F.patch


echo "\n=============="
echo "\"Fix pylint superfluous-parens\" --- Commit rejected to foster better code legibility"
echo "https://github.com/miguelsousa/openbakery/commit/578bd555d51fbebc5c05b634d6a7fde8befe35ac"
echo ""
patch -p1 -R < openbakery/patches/0010-Fix-pylint-superfluous-parens.patch

echo "\n=============="
echo "\"Delete get_regular method\" --- Commit rejected to foster better code legibility"
echo "https://github.com/miguelsousa/openbakery/commit/799c11e36c5f88e89a6eda29f3c545bddfa55135"
echo ""
patch -p1 -R < openbakery/patches/0011-Delete-get_regular-method.patch

echo "\n=============="
echo "\"Remove a few incorrect 'PASS' 2nd args from calls to method 'assert_PASS'"
echo ""
patch -p1 -R < openbakery/patches/0012-remove-the-incorrect-PASS-2nd-arg-from-assert_PASS-c.patch

echo "\n=============="
echo "\"From: Simon Cozens <simon@simon-cozens.org>"
echo "Date: Thu, 15 Jun 2023 08:22:55 +0100"
echo "Subject: Fix an ERROR on italic_angle check"
echo ""
echo "If any of the glyphs checked (bar, vertical line, left square bracket, etc.)"
echo "have no outlines, the check will now emit a WARN, because that's useful information."
echo ""
echo "com.google.fonts/check/italic_angle on OpenType profile"
echo "(PR #4187)"
echo ""
;;;;; ATTENTION: There is no "-R" in the command below!
patch -p1 < openbakery/patches/0013-Fix-an-ERROR-on-italic_angle-check.patch

echo "\n=============="
echo "FontBakery has Sphinx-based docs"
echo ""
patch -p1 -R < openbakery/patches/0014-FontBakery-has-Sphinx-based-docs.patch

echo "\n=============="
echo "Preserve the comment reminding us to someday fix"
echo " command-line autocompletion in a crossplatform manner."
echo ""
patch -p1 -R < openbakery/patches/0015-Preserve-the-comment-reminding-us-to-someday-fix-com.patch

echo "DONE!\n=============="

