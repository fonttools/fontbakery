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


        scripts = [re.sub('\.\w*$', '', f.replace('fontbakery-', '')) for f in \
                   os.listdir(self.bin_path) if f.startswith('fontbakery-')]
        subcommands = subprocess.check_output(['python',
                                               os.path.join('bin', 'fontbakery'),
                                               '--list-subcommands']).split()
        self.assertEqual(sorted(scripts), sorted(subcommands))


class TestFontbakerySubcommands(unittest.TestCase):
    """Functional tests to determine whether each subcommand can execute successfully"""
    def setUp(self):
        self.get_path = lambda name: os.path.join('bin', 'fontbakery-' + name + '.py')
        self.example_dir = os.path.join('data', 'test', 'cabin')
        self.example_font = os.path.join(self.example_dir, 'Cabin-Regular.ttf')
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

    def test_check_googlefonts(self):
        self.check_script(['python', self.get_path('check-googlefonts'), self.example_font])

    # We may someday add more targets here such as 'check-opentype' for generic OpenType spec tests
    # as discussed at https://github.com/googlefonts/fontbakery/issues/1625

if __name__ == '__main__':
    unittest.main()
