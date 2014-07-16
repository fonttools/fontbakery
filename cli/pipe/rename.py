import os.path as op
import re

from cli.system import stdoutlog, shutil
from fontTools import ttLib


class Rename(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        rename_executed = False
        newfiles = []
        for i, filepath in enumerate(pipedata['bin_files']):
            path = op.join(self.builddir, filepath)

            font = ttLib.TTFont(path)

            psname = self.get_psname(font)
            if psname:
                if op.basename(path) != psname:
                    if not rename_executed:
                        self.stdout_pipe.write('Rename built files with PS Naming',
                                               prefix='### ')
                        rename_executed = True
                    shutil.move(path, op.join(op.dirname(path), psname))
                newfiles.append(filepath.replace(op.basename(filepath), psname))
            else:
                newfiles.append(filepath)
        pipedata['bin_files'] = newfiles
        return pipedata

    @staticmethod
    def nameTableRead(font, NameID, fallbackID=None):
        for record in font['name'].names:
            if record.nameID == NameID:
                if b'\000' in record.string:
                    string = record.string.decode('utf-16-be')
                    return string.encode('utf-8')
                else:
                    return record.string
        if fallbackID:
            return Rename.nameTableRead(font, fallbackID)
        return ''

    def get_psname(self, ttfont):
        stylename = re.sub(r'\s', '', self.get_style(ttfont))
        familyname = re.sub(r'\s', '', self.get_family(ttfont))
        return "{}-{}.ttf".format(familyname, stylename)

    def get_style(self, ttfont):
        # Find the style name
        style_name = Rename.nameTableRead(ttfont, 17, 2)
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def get_family(self, ttfont):
        return Rename.nameTableRead(ttfont, 16, 1)
