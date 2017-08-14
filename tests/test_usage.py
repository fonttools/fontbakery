import os
import re
import unittest
import subprocess

class TestSubcommands(unittest.TestCase):

    def setUp(self):
      self.bin_path = os.path.join('bin')

    def test_list_subcommands_has_all_scripts(self):
        """Tests if the output from running fontbakery --list-subcommands matches the
        fontbakery scripts within the bin folder"""

        scripts = [f for f in os.listdir(self.bin_path) if f.startswith('fontbakery-')]
        fontbakery = os.path.join('bin', 'fontbakery')
        subcommands = subprocess.check_output(['python', fontbakery, '--list-subcommands']).split()
        scripts = [re.sub('\.\w*$', '', f.replace('fontbakery-', '')) for f in scripts]

        self.assertEqual(sorted(scripts), sorted(subcommands))

if __name__ == '__main__':
  unittest.main()
