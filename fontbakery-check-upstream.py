#!/usr/bin/env python
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
import argparse
import defusedxml.lxml
# import glob
import logging
import os
# import re
from fontTools import ttLib

# =====================================
# Helper logging class
# TODO: This code is copied from fontbakery-check-ttf.py
# TODO: Deduplicate it by placing it in a shared external file.


class FontBakeryCheckLogger():
    all_checks = []
    current_check = None

    def save_json_report(self, filename="fontbakery-check-results.json"):
        import json
        self.flush()
        json_data = json.dumps(self.all_checks,
                               sort_keys=True,
                               indent=4,
                               separators=(',', ': '))
        open(filename, 'w').write(json_data)
        logging.debug(("Saved check results in "
                       "JSON format to '{}'").format(filename))

    def flush(self):
        if self.current_check is not None:
            self.all_checks.append(self.current_check)

    def new_check(self, desc):
        self.flush()
        logging.debug("Check #{}: {}".format(len(self.all_checks) + 1, desc))
        self.current_check = {"description": desc,
                              "log_messages": [],
                              "result": "unknown"}

    def skip(self, msg):
        logging.info("SKIP: " + msg)
        self.current_check["log_messages"].append(msg)
        self.current_check["result"] = "SKIP"

    def ok(self, msg):
        logging.info("OK: " + msg)
        self.current_check["log_messages"].append(msg)
        if self.current_check["result"] != "FAIL":
            self.current_check["result"] = "OK"

    def warning(self, msg):
        logging.warning(msg)
        self.current_check["log_messages"].append("Warning: " + msg)
        if self.current_check["result"] == "unknown":
            self.current_check["result"] = "WARNING"

    def error(self, msg):
        logging.error(msg)
        self.current_check["log_messages"].append("ERROR: " + msg)
        self.current_check["result"] = "ERROR"

    def hotfix(self, msg):
        logging.info('HOTFIXED: ' + msg)
        self.current_check['log_messages'].append('HOTFIX: ' + msg)
        self.current_check['result'] = "HOTFIX"


# I think that this PiFont and its related classes can be
# refactored into something a bit less verbose and convoluted
class PiFont(object):

    def __init__(self, path):
        """ Supplies common API interface to several font formats """
        self.font = PiFont.open(path)

    @staticmethod
    def open(path):
        """ Return file instance depending on font format

        >>> PiFont.open('tests/fixtures/src/Font-Italic.ufo')
        [PiFontUfo "tests/fixtures/src/Font-Italic.ufo"]
        >>> PiFont.open('tests/fixtures/ttf/Font-Italic.ttf')
        [PiFontFontTools "tests/fixtures/ttf/Font-Italic.ttf"]
        >>> PiFont.open('tests/fixtures/src/Font-Light.sfd')
        [PiFontSFD "tests/fixtures/src/Font-Light.sfd"]
         """
        if path[-4:] == '.ufo':
            return PiFontUfo(path)
        if path[-4:] in ['.ttf', '.otf', '.ttx']:
            return PiFontFontTools(path)
        if path[-4:] == '.sfd':
            return PiFontSFD(path)

    def get_glyph(self, glyphname):
        """ Return glyph instance """
        return self.font.get_glyph(glyphname)

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        Returns:
            :list: List of tuples describing glyphs sorted by glyph code
        """
        return self.font.get_glyphs()

    def get_contours_count(self, glyphname):
        """ Retrieves count of contours, including composites glyphs like "AE"

        Arguments:

            :glyphname string: glyph unicode name

        Returns:
            :int: count of contours
        """
        return self.font.get_contours_count(glyphname)

    def get_points_count(self, glyphname):
        """ Retrieves count of points, including composites glyphs like "AE"

        Arguments:
            :glyphname string: glyph unicode name

        Returns:
            :int: count of points
        """
        return self.font.get_points_count(glyphname)


class PiFontSFD:
    """ Supplies methods used by PiFont class to access SFD """

    def __init__(self, path):
        import fontforge
        self.path = path
        self.font = fontforge.open(path)

    def __repr__(self):
        return '[PiFontSFD "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/src/Font-Light.sfd')
        >>> f.get_glyphs()[:3]
        [(-1, 'caron.alt'), (-1, 'foundryicon'), (2, 'uni0002')]
        """
        ll = self.font.glyphs()
        return sorted(map(lambda x: (x.unicode, x.glyphname), ll))

    def get_contours_count(self, glyphname):
        return 0

    def get_points_count(self, glyphname):
        return 0


class PiFontUfo:
    """ Supplies methods used by PiFont class to access UFO """

    def __init__(self, path):
        import robofab
        self.path = path
        self.font = robofab.world.OpenFont(path)

    def __repr__(self):
        return '[PiFontUfo "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_glyphs()[:3]
        [(2, 'uni0002'), (9, 'uni0009'), (10, 'uni000A')]
        """
        ll = zip(self.font.getCharacterMapping(),
                 map(lambda x: x[0],
                     self.font.getCharacterMapping().values()))
        return sorted(ll)

    def get_glyph(self, glyphname):
        return self.font[glyphname]

    def get_contours_count(self, glyphname):
        """ Retrieves count of glyph contours

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_contours_count('AEacute')
        3
        """
        value = 0
        components = self.font[glyphname].getComponents()
        if components:
            for component in components:
                value += self.get_contours_count(component.baseGlyph)

        contours = self.font[glyphname].contours
        if contours:
            value += len(contours)
        return value

    def get_points_count(self, glyphname):
        """ Retrieves count of glyph points in contours

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_points_count('AEacute')
        24
        """
        value = 0
        components = self.font[glyphname].getComponents()
        if components:
            for component in components:
                value += self.get_points_count(component.baseGlyph)

        contours = self.font[glyphname].contours
        if contours:
            for contour in contours:
                value += len(contour.segments)
        return value


class PiFontFontTools:
    """ Supplies methods used by PiFont class to access TTF """

    def __init__(self, path):
        logging.debug('loading font from path = "{}"...'.format(path))
        self.path = path
        if path[-4:] == '.ttx':
            self.font = ttLib.TTFont(None)
            self.font.importXML(path, quiet=True)
        else:
            self.font = ttLib.TTFont(path)

    def __repr__(self):
        return '[PiFontFontTools "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/ttf/Font-Italic.ttf')
        >>> f.get_glyphs()[:3]
        [(32, 'space'), (33, 'exclam'), (34, 'quotedbl')]
        """

        cmap4 = None
        for table in self.font['cmap'].tables:
            if table.format == 4:
                cmap4 = table.cmap

        if cmap4 is not None:
            ll = zip(cmap4, cmap4.values())
            return sorted(ll)
        else:
            return None

    def get_contours_count(self, glyphname):
        return 0

    def get_points_count(self, glyphname):
        return 0


class UpstreamDirectory(object):
    """ Describes structure of upstream directory

    >>> upstream = UpstreamDirectory("tests/fixtures/upstream-example")
    >>> upstream.UFO
    ['Font-Regular.ufo']
    >>> upstream.TTX
    ['Font-Light.ttx']
    >>> upstream.BIN
    ['Font-SemiBold.ttf']
    >>> upstream.METADATA
    ['METADATA.pb']
    >>> sorted(upstream.LICENSE)
    ['APACHE.txt', 'LICENSE.txt']
    >>> upstream.SFD
    ['Font-Bold.sfd']
    >>> sorted(upstream.TXT)
    ['APACHE.txt', 'LICENSE.txt']
    """

    OFL = ['open font license.markdown', 'ofl.txt', 'ofl.md']
    LICENSE = ['license.txt', 'license.md', 'copyright.txt']
    APACHE = ['apache.txt', 'apache.md']
    UFL = ['ufl.txt', 'ufl.md']

    ALL_LICENSES = OFL + LICENSE + APACHE + UFL

    def __init__(self, upstream_path):
        self.upstream_path = upstream_path

        self.UFO = []
        self.TTX = []
        self.BIN = []
        self.LICENSE = []
        self.METADATA = []
        self.SFD = []
        self.TXT = []

        self.walk()

    def get_ttx(self):
        return self.TTX

    def get_binaries(self):
        return self.BIN

    def get_fonts(self):
        return self.UFO + self.TTX + self.BIN + self.SFD
    ALL_FONTS = property(get_fonts)

    def walk(self):
        l = len(self.upstream_path)
        exclude = ['build_info', ]
        for root, dirs, files in os.walk(self.upstream_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                fullpath = os.path.join(root, f)

                if f[-4:].lower() == '.ttx':
                    try:
                        doc = defusedxml.lxml.parse(fullpath)
                        el = doc.xpath('//ttFont[@sfntVersion]')
                        if not el:
                            continue
                    except Exception as exc:
                        msg = 'Failed to parse "{}". Error: {}'
                        logging.error(msg.format(fullpath, exc))
                        continue
                    self.TTX.append(fullpath[l:].strip('/'))

                if os.path.basename(f).lower() == 'metadata.pb':
                    self.METADATA.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.ttf', '.otf']:
                    self.BIN.append(fullpath[l:].strip('/'))

                if f[-4:].lower() == '.sfd':
                    self.SFD.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.txt', '.markdown', '.md', '.LICENSE']:
                    self.TXT.append(fullpath[l:].strip('/'))

                if os.path.basename(f).lower()\
                   in UpstreamDirectory.ALL_LICENSES:
                    self.LICENSE.append(fullpath[l:].strip('/'))

            for d in dirs:
                fullpath = os.path.join(root, d)
                if os.path.splitext(fullpath)[1].lower() == '.ufo':
                    self.UFO.append(fullpath[l:].strip('/'))

fb = FontBakeryCheckLogger()


def upstream_checks():
    # set up some command line argument processing
    description = 'Runs checks or tests on specified upstream folder(s)'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folders', nargs="+",
                        help="Test folder(s), can be a list")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Verbosity level", default=False)
    args = parser.parse_args()

    # set up a basic logging config
    logger = logging.getLogger()
    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    folders_to_check = []
    for f in args.folders:
        if os.path.isdir(f):
            folders_to_check.append(f)
        else:
            fb.error("'{}' is not a valid existing folder.".format(f))
            continue

    if len(folders_to_check) == 0:
        fb.error("None of the specified paths "
                 "seem to be existing folders.")
        exit(-1)

    for folder in folders_to_check:
        directory = UpstreamDirectory(folder)

# ---------------------------------------------------------------------
#        fb.new_check("Each font in family has matching glyph names?")
#        # TODO: This check seems broken. Must be revied!
#        # TODO:  does this glyphs list object get populated?
#        glyphs = []
#        failed = False
#        for f in directory.get_fonts():
#            try:
#                font = PiFont(os.path.join(folder, f))
#                if glyphs and glyphs != font.get_glyphs():
#                    # TODO report which font
#                    failed = True
#                    fb.error('Family has different glyphs across fonts')
#            except:
#                failed = True
#                fb.error("Failed to load font file: '{}'".format(f))
#
#        if failed is False:
#            fb.ok("All fonts in family have matching glyph names.")

# ---------------------------------------------------------------------
        fb.new_check("Glyphs have same number"
                     " of contours across family ?")
        glyphs = {}
        failed = False
        for f in directory.get_fonts():
            font = PiFont(os.path.join(folder, f))
            for glyphcode, glyphname in font.get_glyphs():
                contours = font.get_contours_count(glyphname)
                if glyphcode in glyphs and glyphs[glyphcode] != contours:
                    failed = True
                    fb.error(("Number of contours of glyph '{}'"
                              " does not match."
                              " Expected {} contours, but actual is"
                              " {} contours").format(glyphname,
                                                     glyphs[glyphcode],
                                                     contours))
                glyphs[glyphcode] = contours
        if failed is False:
            fb.ok("Glyphs have same number of contours across family.")

# ---------------------------------------------------------------------
        fb.new_check("Glyphs have same"
                     " number of points across family ?")
        glyphs = {}
        failed = False
        for f in directory.get_fonts():
            font = PiFont(os.path.join(folder, f))
            for g, glyphname in font.get_glyphs():
                points = font.get_points_count(glyphname)
                if g in glyphs and glyphs[g] != points:
                    failed = True
                    fb.error(("Number of points of glyph '{}' does not match."
                              " Expected {} points, but actual is "
                              "{} points").format(glyphname,
                                                  glyphs[g],
                                                  points))
                glyphs[g] = points
        if failed is False:
            fb.ok("Glyphs have same"
                  " number of points across family.")

# ======================================================================
        def assertExists(folderpath, filenames, err_msg, ok_msg):
            if not isinstance(filenames, list):
                filenames = [filenames]

            missing = []
            for filename in filenames:
                fullpath = os.path.join(folderpath, filename)
                if os.path.exists(fullpath):
                    missing.append(fullpath)
            if len(missing) > 0:
                fb.error(err_msg.format(", ".join(missing)))
            else:
                fb.ok(ok_msg)

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain COPYRIGHT file ?")
        assertExists(f, "COPYRIGHT.txt",
                     "Font folder lacks a copyright file at '{}'",
                     "Font folder contains COPYRIGHT.txt")

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain a DESCRIPTION file ?")
        assertExists(f, "DESCRIPTION.en_us.html",
                     "Font folder lacks a description file at '{}'",
                     "Font folder should contain DESCRIPTION.en_us.html.")

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain licensing files?")
        assertExists(f, ["LICENSE.txt", "OFL.txt"],
                     "Font folder lacks licensing files at '{}'",
                     "Font folder should contain licensing files.")

# ---------------------------------------------------------------------
        fb.new_check("Font folder should contain FONTLOG.txt")
        assertExists(f, "FONTLOG.txt",
                     "Font folder lacks a fontlog file at '{}'",
                     "Font folder should contain a 'FONTLOG.txt' file.")

# =======================================================================
# Tests for common upstream repository files.
# note:
# This test case is not related to font processing. It makes only common
# checks like one - test that upstream repository contains METADATA.pb)
# =======================================================================

# ---------------------------------------------------------------------
        fb.new_check("Repository contains METADATA.pb file?")
        fullpath = os.path.join(f, 'METADATA.pb')
        if not os.path.exists(fullpath):
            fb.error("File 'METADATA.pb' does not exist"
                     " in root of upstream repository")
        else:
            fb.ok("Repository contains METADATA.pb file.")

# ---------------------------------------------------------------------
#        fb.new_check("Copyright notice consistent "
#                     "across all fonts in this family?")
#        ufo_dirs = []
#        for root, dirs, files in os.walk(self.operator.path):
#            for d in dirs:
#                fullpath = os.path.join(root, d)
#                if os.path.splitext(fullpath)[1].lower() == '.ufo':
#                    ufo_dirs.append(fullpath)
#
#        copyright = None
#        for ufo_folder in ufo_dirs:
#            current_notice = self.lookup_copyright_notice(ufo_folder)
#            if current_notice is None:
#                continue
#            if copyright is not None and current_notice != copyright:
#                self.fail('"%s" != "%s"' % (current_notice, copyright))
#                break
#            copyright = current_notice
#
#        COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)
#        def grep_copyright_notice(self, contents):
#            match = COPYRIGHT_REGEX.search(contents)
#            if match:
#                return match.group(0).strip(',\r\n')
#            return
#
#        def lookup_copyright_notice(self, ufo_folder):
#            current_path = ufo_folder
#            try:
#                contents = open(os.path.join(ufo_folder,
#                                             'fontinfo.plist')).read()
#                copyright = self.grep_copyright_notice(contents)
#                if copyright:
#                    return copyright
#            except (IOError, OSError):
#                pass
#
#            while os.path.realpath(self.operator.path) != current_path:
#                # look for all text files inside folder
#                # read contents from them and compare with copyright notice
#                # pattern
#                files = glob.glob(os.path.join(current_path, '*.txt'))
#                files += glob.glob(os.path.join(current_path, '*.ttx'))
#                for filename in files:
#                    with open(os.path.join(current_path, filename)) as fp:
#                        match = COPYRIGHT_REGEX.search(fp.read())
#                        if not match:
#                           continue
#                        return match.group(0).strip(',\r\n')
#                current_path = os.path.join(current_path, '..')  # go up
#                current_path = os.path.realpath(current_path)
#            return

        fb.save_json_report("fontbakery-check-upstream-results.json")

if __name__ == '__main__':
    upstream_checks()
