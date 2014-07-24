import os.path as op

from checker.base import BakeryTestCase as TestCase, tags


class CheckTextFilesExist(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def assertExists(self, filename):
        if not op.exists(op.join(op.dirname(self.path), filename)):
            self.fail('%s does not exist in project' % filename)

    @tags('required')
    def test_copyrighttxt_exists(self):
        """ Font folder should contains COPYRIGHT.txt """
        self.assertExists('COPYRIGHT.txt')

    @tags('required')
    def test_description_exists(self):
        """ Font folder should contains DESCRIPTION.en_us.html """
        self.assertExists('DESCRIPTION.en_us.html')

    @tags('required')
    def test_licensetxt_exists(self):
        """ Font folder should contains LICENSE.txt """
        # TODO: This should be OFL.txt or LICENSE.txt
        self.assertExists('LICENSE.txt')

    def test_fontlogtxt_exists(self):
        """ Font folder should contains FONTLOG.txt """
        self.assertExists('FONTLOG.txt')
