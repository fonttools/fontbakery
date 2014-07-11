# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import fontforge
import os.path as op
import plistlib
import re
import sys

from fontTools import ttLib
from cli.system import shutil, run


class FontSourceAbstract(object):
    """ Abstract class to provide copy functional in baking process

        Inherited classes must implement `open_source` method
        and properties `style_name` and `family_name`. """

    def __init__(self, path, stdout_pipe=None):
        self.source = self.open_source(path)
        self.source_path = path
        self.stdout_pipe = stdout_pipe or sys.stdout

    def open_source(self, sourcepath):
        raise NotImplementedError

    @property
    def style_name(self):
        raise NotImplementedError

    @property
    def family_name(self):
        raise NotImplementedError

    def before_copy(self):
        """ If method returns False then bakery process halted. Default: True.

            Implement this if you need additional check before source
            path will be copied.

            Good practice to call inside self.stdout_pipe.write() method
            to make user know what is wrong with source. """
        return True

    def copy(self, destdir):
        """ Copy source file to destination directory.

            File can be renamed if family name and style different
            to original filename. See naming recommendation:
            http://forum.fontlab.com/index.php?topic=313.0 """
        destpath = op.join(destdir, self.get_file_name())

        if op.isdir(self.source_path):
            shutil.copytree(self.source_path, destpath,
                            log=self.stdout_pipe)
        else:
            shutil.copy(self.source_path, destpath,
                        log=self.stdout_pipe)

    def get_file_name(self):
        return self.postscript_fontname + self.source_path[-4:]

    @property
    def postscript_fontname(self):
        stylename = re.sub(r'\s', '', self.style_name)
        familyname = re.sub(r'\s', '', self.family_name)
        return "{}-{}".format(familyname, stylename)

    def after_copy(self, builddir):
        return


class UFOFontSource(FontSourceAbstract):

    def open_source(self, path):
        return plistlib.readPlist(op.join(path, 'fontinfo.plist'))

    @property
    def style_name(self):
        # Get the styleName
        style_name = self.source['styleName']
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def family_name():
        doc = "The family_name property."

        def fget(self):
            pfn = self.source.get('openTypeNamePreferredFamilyName', '')
            return (self._family_name or pfn
                    or self.source.get('familyName', ''))

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name

        return locals()
    family_name = property(**family_name())

    def before_copy(self):
        if not self.family_name:
            _ = ('[MISSED] Please set openTypeNamePreferredFamilyName or '
                 'familyName in %s fontinfo.plist and run another'
                 ' bake process.') % self.source_path
            self.stdout_pipe.write(_, prefix='### ')
            return False
        return True

    def convert_ufo2ttf(self, builddir):
        from scripts.font2ttf import convert
        _ = '$ font2ttf.py %s %s %s'
        self.stdout_pipe.write(_ % (self.source_path,
                                    self.postscript_fontname + '.ttf',
                                    self.postscript_fontname + '.otf'))

        ufopath = op.join(builddir, 'sources', self.get_file_name())
        ttfpath = op.join(builddir, self.postscript_fontname + '.ttf')
        otfpath = op.join(builddir, self.postscript_fontname + '.otf')

        try:
            convert(ufopath, ttfpath, otfpath, log=self.stdout_pipe)
        except Exception, ex:
            self.stdout_pipe.write('# Error: %s\n' % ex.message)

    def optimize_ttx(self, builddir):
        filename = self.postscript_fontname
        # convert the ttf to a ttx file - this may fail
        font = fontforge.open(op.join(builddir, filename) + '.ttf')
        glyphs = []
        for g in font.glyphs():
            if not g.codepoint:
                continue
            glyphs.append(g.codepoint)

        from fontTools import subset
        args = [op.join(builddir, filename) + '.ttf'] + glyphs
        # args += ['--notdef-outline', '--name-IDs="*"', '--hinting']
        subset.main(args)

        self.stdout_pipe.write(' '.join(args))

        # compare filesizes TODO print analysis of this :)
        cmd = "ls -l '%s.ttf'*" % filename
        run(cmd, cwd=builddir, log=self.stdout_pipe)

        # move ttx files to src
        shutil.move(op.join(builddir, filename + '.ttf.subset'),
                    op.join(builddir, filename + '.ttf'),
                    log=self.stdout_pipe)

    def after_copy(self, builddir):
        # If we rename, change the font family name metadata
        # inside the _out_ufo
        if self.family_name:
            # Read the _out_ufo fontinfo.plist
            _out_ufo_path = op.join(builddir, 'sources', self.get_file_name())
            _out_ufoPlist = op.join(_out_ufo_path, 'fontinfo.plist')
            _out_ufoFontInfo = plistlib.readPlist(_out_ufoPlist)
            # Set the familyName
            _out_ufoFontInfo['familyName'] = self.family_name

            # Set PS Name
            # Ref: www.adobe.com/devnet/font/pdfs/5088.FontNames.pdf‎
            # < Family Name > < Vendor ID > - < Weight > < Width >
            # < Slant > < Character Set >
            psfn = self.postscript_fontname
            _out_ufoFontInfo['postscriptFontName'] = psfn
            _out_ufoFontInfo['postscriptFullName'] = psfn.replace('-', ' ')
            # Write _out fontinfo.plist
            plistlib.writePlist(_out_ufoFontInfo, _out_ufoPlist)

        self.convert_ufo2ttf(builddir)
        self.optimize_ttx(builddir)


class TTXFontSource(FontSourceAbstract):

    @staticmethod
    def nameTableRead(font, NameID, fallbackNameID=False):
        for record in font['name'].names:
            if record.nameID == NameID:
                if b'\000' in record.string:
                    string = record.string.decode('utf-16-be')
                    return string.encode('utf-8')
                else:
                    return record.string

        if fallbackNameID:
            return TTXFontSource.nameTableRead(font, fallbackNameID)

    def open_source(self, path):
        font = ttLib.TTFont(None, lazy=False, recalcBBoxes=True,
                            verbose=False, allowVID=False)
        font.importXML(path, quiet=True)
        return font

    def copy(self, destdir):
        import glob
        super(TTXFontSource, self).copy(destdir)
        rootpath = op.dirname(self.source_path)
        fontname = op.basename(self.source_path)
        for f in glob.glob(op.join(rootpath, '%s.*.ttx' % fontname[:-4])):
            fontpath = op.join(rootpath, f)
            shutil.copy(fontpath, op.join(destdir, fontpath), log=self.stdout_pipe)

    @property
    def style_name(self):
        # Find the style name
        style_name = TTXFontSource.nameTableRead(self.source, 17, 2)
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def family_name():
        doc = "The family_name property."

        def fget(self):
            return (self._family_name
                    or TTXFontSource.nameTableRead(self.source, 16, 1))

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name

        return locals()
    family_name = property(**family_name())

    def compile_ttx(self, builddir):
        run("ttx {}.ttx".format(self.postscript_fontname),
            cwd=op.join(builddir, 'sources'),
            log=self.stdout_pipe)

    def convert_otf2ttf(self, builddir):
        _ = '$ font2ttf.py {0}.otf {0}.ttf\n'
        self.stdout_pipe.write(_.format(self.postscript_fontname))
        from scripts.font2ttf import convert
        try:
            path = op.join(builddir, 'sources',
                           self.postscript_fontname + '.otf')
            ttfpath = op.join(builddir, self.postscript_fontname + '.ttf')
            convert(path, ttfpath, log=self.stdout_pipe)
        except Exception, ex:
            self.stdout_pipe.write('Error: %s\n' % ex.message)

    def after_copy(self, builddir):
        out_name = self.postscript_fontname + '.ttf'

        self.compile_ttx(builddir)

        if self.source.sfntVersion == 'OTTO':  # OTF
            self.convert_otf2ttf(builddir)
        # If TTF already, move it up
        else:
            try:
                shutil.move(op.join(builddir, 'sources', out_name),
                            op.join(builddir, out_name),
                            log=self.stdout_pipe)
            except (OSError, IOError):
                pass


class BINFontSource(TTXFontSource):

    def open_source(self, path):
        return ttLib.TTFont(path, lazy=False, recalcBBoxes=True,
                            verbose=False, allowVID=False)

    def compile_ttx(self, builddir):
        """ Override TTXFontSource compile_ttx method as BINFontSource
            based on compiled already fonts """
        pass


class SFDFontSource(FontSourceAbstract):

    def open_source(self, path):
        return fontforge.open(path)

    def family_name():
        doc = "The family_name property."

        def fget(self):
            return self._family_name or self.source.sfnt_names[1][2]

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name
        return locals()
    family_name = property(**family_name())

    @property
    def style_name(self):
        return self.source.sfnt_names[2][2]

    def after_copy(self, builddir):
        from scripts.font2ttf import convert
        _ = '$ font2ttf.py %s %s %s'
        self.stdout_pipe.write(_ % (self.source_path,
                                    self.postscript_fontname + '.ttf',
                                    self.postscript_fontname + '.otf'))

        ufopath = op.join(builddir, 'sources', self.get_file_name())
        ttfpath = op.join(builddir, self.postscript_fontname + '.ttf')
        otfpath = op.join(builddir, self.postscript_fontname + '.otf')

        try:
            convert(ufopath, ttfpath, otfpath, log=self.stdout_pipe)
        except Exception, ex:
            self.stdout_pipe.write('FAILED\nError: %s\n' % ex.message)


def get_fontsource(path, log):
    """ Returns instance of XXXFontSource class based on path extension.

        It supports only four XXXFontSource classes for the moment:

        >>> get_fontsource('test.ufo')
        <UFOFontSource instance>

        >>> get_fontsource('test.ttx')
        <TTXFontSource instance>

        >>> get_fontsource('test.ttf')
        <BINFontSource instance>

        >>> get_fontsource('test.otf')
        <BINFontSource instance>

        >>> get_fontsource('test.sfd')
        <SFDFontSource instance>
    """
    if path.endswith('.ufo'):
        return UFOFontSource(path, log)
    elif path.endswith('.ttx'):
        return TTXFontSource(path, log)
    elif path.endswith('.ttf') or path.endswith('.otf'):
        return BINFontSource(path, log)
    elif path.endswith('.sfd'):
        return SFDFontSource(path, log)
    else:
        log.write('[MISSED] Unsupported sources file: %s\n' % path,
                  prefix='Error: ')
