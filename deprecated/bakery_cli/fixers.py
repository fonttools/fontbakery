
class AddSPUAByGlyphIDToCmap(Fixer):

    def get_shell_command(self):
        SCRIPTPATH = 'fontbakery-fix-glyph-private-encoding.py'
        return "{0} --autofix {1}".format(SCRIPTPATH, self.fontpath)

    def fix(self):
        unencoded_glyphs = get_unencoded_glyphs(self.font)
        if not unencoded_glyphs:
            return

        ucs2cmap = None
        cmap = self.font["cmap"]

        # Check if an UCS-2 cmap exists
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            ucs2cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if ucs2cmap:
                break
        # Create UCS-4 cmap and copy the contents of UCS-2 cmap
        # unless UCS 4 cmap already exists
        ucs4cmap = cmap.getcmap(3, 10)
        if not ucs4cmap:
            cmapModule = fontTools.ttLib.getTableModule('cmap')
            ucs4cmap = cmapModule.cmap_format_12(12)
            ucs4cmap.platformID = 3
            ucs4cmap.platEncID = 10
            ucs4cmap.language = 0
            if ucs2cmap:
                ucs4cmap.cmap = copy.deepcopy(ucs2cmap.cmap)
            cmap.tables.append(ucs4cmap)
        # Map all glyphs to UCS-4 cmap Supplementary PUA-A codepoints
        # by 0xF0000 + glyphID
        ucs4cmap = cmap.getcmap(3, 10)
        for glyphID, glyph in enumerate(self.font.getGlyphOrder()):
            if glyph in unencoded_glyphs:
                ucs4cmap.cmap[0xF0000 + glyphID] = glyph
        self.font['cmap'] = cmap
        return True


def get_unencoded_glyphs(ttx):
    """ Check if font has unencoded glyphs """
    cmap = ttx['cmap']

    new_cmap = cmap.getcmap(3, 10)
    if not new_cmap:
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            new_cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if new_cmap:
                break

    if not new_cmap:
        return []

    diff = list(set(ttx.glyphOrder) - set(new_cmap.cmap.values()) - {'.notdef'})
    return [g for g in diff[:] if g != '.notdef']


class GaspFixer(Fixer):

    def get_shell_command(self):
        SCRIPTPATH = 'fontbakery-fix-gasp.py'
        return "$ {0} --set={1} {2}".format(SCRIPTPATH, 15, self.fontpath)

    def fix(self, value=15):
        try:
            table = self.font.get('gasp')
            table.gaspRange[65535] = value
            return True
        except:
            logger.error('ER: {}: no table gasp'.format(self.fontpath))
            return

    def show(self, path):
        try:
            table = self.font.get('gasp')
        except:
            logger.error('ER: {}: no table gasp'.format(path))
            return

        try:
            logger.info(self.font.get('gasp').gaspRange[65535])
        except IndexError:
            logger.error('ER: {}: no index 65535'.format(path))


class OpentypeFamilyNameFixer(Fixer):
    def fix(self):
        fontfile = os.path.basename(self.fontpath)
        font = Font(ttfont=self.font)
        font.ot_family_name = font.familyname
        logger.error('OK: {}: Fixed: Windows-only Opentype-specific FamilyName set to "{}"'.format(fontfile, font.familyname))
        return True


class OpentypeFullnameFixer(Fixer):
    def fix(self):
        fontfile = os.path.basename(self.fontpath)
        font = Font(ttfont=self.font)
        font.ot_full_name = font.fullname
        logger.error('OK: {}: Fixed: Windows-only Opentype-specific FullName set to "{}"'.format(fontfile, font.fullname))
        return True


class SubfamilyNameFixer(Fixer):
    def fix(self):
        fontfile = os.path.basename(self.fontpath)
        suggestedvalues = getSuggestedFontNameValues(self.font)
        font.familyname = suggestedvalues['family']
        font.stylename = suggestedvalues['subfamily']
        logger.error('OK: {}: Fixed: family name set to "{}" and sub-family name set to "{}"'.format(fontfile,
            suggestedvalues['family'], suggestedvalues['subfamily']))
        return True


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
DATA_DIR = os.path.abspath(DATA_DIR)


class LicenseInfoURLFixer(Fixer):

    def get_licenseurl_filename(self):
        return None

    def get_licensecontent_filename(self):
        return None

    def get_licensecontent(self):
        path = os.path.join(DATA_DIR, self.get_licensecontent_filename())
        return open(path).read()

    def validate(self):
        licenseText = self.get_licensecontent()
        path = os.path.join(DATA_DIR, self.get_licenseurl_filename())
        placeholder = open(path).read().strip()

        for field in self.font['name'].names:
            if field.nameID == NAMEID_LICENSE_INFO_URL:
                string = field.string.decode(field.getEncoding())

                if string != placeholder:
                    return placeholder

            if field.nameID == NAMEID_LICENSE_DESCRIPTION:
                string = field.string.decode(field.getEncoding())

                if licenseText.strip() in string:
                    return placeholder
        return

    def fix(self):
        placeholder = self.validate()
        if not placeholder:
            return

        for nameRecord in self.font['name'].names:
            if nameRecord.nameID == NAMEID_LICENSE_INFO_URL:
                nameRecord.string = placeholder.encode(placeholder.getEncoding())
        return True


class OFLLicenseInfoURLFixer(LicenseInfoURLFixer):

    def get_licenseurl_filename(self):
        return 'OFL.url'

    def get_licensecontent_filename(self):
        return 'OFL.license'


class ApacheLicenseInfoURLFixer(LicenseInfoURLFixer):

    def get_licenseurl_filename(self):
        return 'APACHE.url'

    def get_licensecontent_filename(self):
        return 'APACHE.license'


class LicenseDescriptionFixer(Fixer):

    def get_placeholder(self):
        path = self.get_placeholder_filename()
        with open(os.path.join(DATA_DIR, path)) as fp:
            return fp.read().strip()

    def fix(self):
        placeholder = self.get_placeholder()
        for nameRecord in self.font['name'].names:
            if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
                nameRecord.string = placeholder.encode(placeholder.getEncoding())
        return True


class OFLLicenseDescriptionFixer(LicenseDescriptionFixer):

    def get_placeholder_filename(self):
        return 'OFL.placeholder'


class ApacheLicenseDescriptionFixer(LicenseDescriptionFixer):

    def get_placeholder_filename(self):
        return 'APACHE.placeholder'

