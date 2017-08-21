"""Unittests to check the functionality of Fontbakery"""
import os
import re
import unittest
import subprocess


class TestSubcommands(unittest.TestCase):
    """Functional tests to determine that bin/fontbakery runs correctly"""
    def setUp(self):
        self.bin_path = os.path.join('bin')
        self.maxDiff = None

    def test_list_subcommands_has_all_scripts(self):
        """Tests if the output from running fontbakery --list-subcommands matches the
        fontbakery scripts within the bin folder"""

        scripts = [f for f in os.listdir(self.bin_path) if f.startswith('fontbakery-')]
        fontbakery = os.path.join('bin', 'fontbakery')
        subcommands = subprocess.check_output(['python', fontbakery, '--list-subcommands']).split()
        scripts = [re.sub('\.\w*$', '', f.replace('fontbakery-', '')) for f in scripts]

        self.assertEqual(sorted(scripts), sorted(subcommands))


class TestFontbakeryScripts(unittest.TestCase):
    """Functional tests to determine whether each script can execute successfully"""
    def setUp(self):
        self.get_path = lambda name: os.path.join('bin', 'fontbakery-' + name + '.py')
        self.example_dir = os.path.join('data', 'test', 'cabin')
        self.example_font = os.path.join(self.example_dir, 'Cabin-Regular.ttf')
        self.blacklisted_scripts = [
          ['python', self.get_path('build-contributors')],  # requires source folder of git commits
          ['python', self.get_path('check-gf-github')],  # Requires github credentials
          ['python', self.get_path('build-font2ttf')],  # Requires fontforge
          ['python', self.get_path('generate-glyphdata')],  # Generates desired_glyph_data.json
          ['python', self.get_path('metadata-vs-api')],  # Requires an API key
          ['python', self.get_path('update-version')],  # Needs to know the current font version and the next version to set
        ]
        self.dir_before_tests = os.listdir(self.example_dir)

    def tearDown(self):
        """Clears the example folder of any files created during the unit tests"""
        files_to_delete = set(os.listdir(self.example_dir)) - set(self.dir_before_tests)
        for f in files_to_delete:
            os.remove(os.path.join(self.example_dir, f))

    def check_script(self, command):
        """Template for unit testing the python scripts"""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertNotIn('Err', stderr, ' '.join(command) + ':\n\n' + stderr)

    def test_build_fontmetadata(self):
        self.check_script(['python', self.get_path('build-fontmetadata'), self.example_font])

    def test_build_ofl(self):
        self.check_script(['python', self.get_path('build-ofl'), self.example_dir])

    def test_check_bbox(self):
        self.check_script(['python', self.get_path('check-bbox'), self.example_font, '--glyphs', '--extremes'])

    def test_check_font_version(self):
        self.check_script(['python', self.get_path('check-font-version'), self.example_font])

    def test_check_googlefonts(self):
        self.check_script(['python', self.get_path('check-googlefonts'), self.example_font])

    def test_check_name(self):
        self.check_script(['python', self.get_path('check-name'), self.example_font])

    def test_check_vtt_compatibility(self):
        self.check_script(['python', self.get_path('check-vtt-compatibility'), self.example_font, self.example_font])

    def test_famil_html_snippet(self):
        self.check_script(['python', self.get_path('family-html-snippet'), 'Roboto', 'test', '--subsets', 'greek'])

    def test_fix_ascii_fontmetadata(self):
        self.check_script(['python', self.get_path('fix-ascii-fontmetadata'), self.example_font])

    def test_fix_cmap(self):
        self.check_script(['python', self.get_path('fix-cmap'), self.example_font])

    def test_fix_dsig(self):
        self.check_script(['python', self.get_path('fix-dsig'), self.example_font])

    def test_fix_familymetadata(self):
        self.check_script(['python', self.get_path('fix-familymetadata'), self.example_font])

    def test_fix_fsselection(self):
        self.check_script(['python', self.get_path('fix-fsselection'), self.example_font])

    def test_fix_fstype(self):
        self.check_script(['python', self.get_path('fix-fstype'), self.example_font])

    def test_fix_gasp(self):
        self.check_script(['python', self.get_path('fix-gasp'), self.example_font])

    def test_fix_glyph_private_encoding(self):
        self.check_script(['python', self.get_path('fix-glyph-private-encoding'), self.example_font])

    def test_fix_glyphs(self):
        self.check_script(['python', self.get_path('fix-glyphs')])

    def test_fix_nameids(self):
        self.check_script(['python', self.get_path('fix-nameids'), self.example_font])

    def test_fix_nonhinting(self):
        self.check_script(['python', self.get_path('fix-nonhinting'), self.example_font, self.example_font + '.fix'])

    def test_fix_ttfautohint(self):
        self.check_script(['python', self.get_path('fix-ttfautohint'), self.example_font])

    def test_fix_vendorid(self):
        self.check_script(['python', self.get_path('fix-vendorid'), self.example_font])

    def test_fix_vertical_metrics(self):
        self.check_script(['python', self.get_path('fix-vertical-metrics'), self.example_font])

    def test_list_panose(self):
        self.check_script(['python', self.get_path('list-panose'), self.example_font])

    def test_list_variable_source(self):
        self.check_script(['python', self.get_path('list-variable-source')])

    def test_list_weightclass(self):
        self.check_script(['python', self.get_path('list-weightclass'), self.example_font])

    def test_list_widthclass(self):
        self.check_script(['python', self.get_path('list-widthclass'), self.example_font])

    def test_nametable_from_filename(self):
        self.check_script(['python', self.get_path('nametable-from-filename'), self.example_font])

# Temporarily disabling this until we close issue #1514
# (https://github.com/googlefonts/fontbakery/issues/1514)
# See also https://github.com/googlefonts/fontbakery/issues/1535
#    def test_update_families(self):
#        self.check_script(['python', self.get_path('update-families'), self.example_font])

    def test_update_nameids(self):
        self.check_script(['python', self.get_path('update-nameids'), self.example_font])


if __name__ == '__main__':
    unittest.main()
