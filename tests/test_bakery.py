import unittest
from mock import patch
from cli.pipe.copy import Copy
from cli.pipe.build import Build
from cli.pipe.rename import Rename
import cli.system


class TestBakery(unittest.TestCase):

    def test_copy_process(self):
        pipedata = {'process_files': ['1.in/fontname-bold.ttx'],
                    'builddir': 'build',
                    'project_root': ''}

        b = Copy('', 'build')
        with patch.object(b, 'copy_to_builddir') as mock_copy2builddir:
            mock_copy2builddir.return_value = 'sources'

            pipedata = b.execute(pipedata)

            mock_copy2builddir.assert_called_once_with(['1.in/fontname-bold.ttx'])
            self.assertEqual(pipedata['process_files'], ['sources/fontname-bold.ttx'])

    def test_copy_with_splitted_ttx(self):
        pipedata = {'process_files': ['1.in/fontname-bold.ttx'],
                    'builddir': 'build',
                    'project_root': ''}

        b = Copy('', 'build')
        with patch.object(b, 'copy_to_builddir') as copy2builddir:
            with patch.object(b, 'lookup_splitted_ttx') as splitted_ttx:
                splitted_ttx.return_value = ['1.in/fontname-bold._g_p_o_s.ttx']
                copy2builddir.return_value = 'sources'

                pipedata = b.execute(pipedata)

                copy2builddir.assert_called_once_with(['1.in/fontname-bold.ttx',
                                                       '1.in/fontname-bold._g_p_o_s.ttx'])
                self.assertEqual(pipedata['process_files'], ['sources/fontname-bold.ttx'])

    def test_convert(self):
        pipedata = {'process_files': ['sources/fontname-bold.ttx',
                                      'sources/fontname-regular.ttx'],
                    'project_root': '',
                    'builddir': 'build'}
        b = Build('', 'build')
        with patch.object(b, "execute_ttx") as ttx_call:
            with patch.object(b, "movebin_to_builddir") as move:
                move.return_value = ['fontname-bold.ttf',
                                     'fontname-regular.ttf']
                pipedata = b.execute(pipedata)

                ttx_call.assert_called_once_with('', 'build',
                                                 ['sources/fontname-bold.ttx',
                                                  'sources/fontname-regular.ttx'])
                self.assertEqual(pipedata['bin_files'],
                                 ['fontname-bold.ttf', 'fontname-regular.ttf'])
                move.assert_called_once_with('build', ['sources/fontname-bold.ttx',
                                                       'sources/fontname-regular.ttx'])

    def test_rename(self):
        pipedata = {'bin_files': ['sources/fontname-bold.ttf']}
        b = Rename('', '')

        with patch.object(b, 'get_psname') as getpsname:
            with patch('cli.system.shutil.move') as move:
                with patch('fontTools.ttLib.TTFont') as TTFont:
                    TTFont.return_value = ''
                    getpsname.return_value = 'fontname-regular.ttf'
                    b.execute(pipedata)
                    move.assert_called_once_with('sources/fontname-bold.ttf',
                                                 'sources/fontname-regular.ttf',
                                                 cli.system.stdoutlog)
        self.assertEqual(pipedata['bin_files'], ['sources/fontname-regular.ttf'])

