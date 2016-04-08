
class MultipleDesignerFixer(Fixer):

    def get_shell_command(self):
        return 'fontbakery-fix-metadata-designer.py {}'.format(self.fontpath)

    def loadfont(self, fontpath):
        pass

    def save(self):
        pass

    def is_valid(self):
        content = {}
        with io.open(self.fontpath, 'r', encoding="utf-8") as fp:
            content = json.load(fp, object_pairs_hook=collections.OrderedDict)

        if len(content.get('designer', '').split()) > 4:
            logger.error('ER: Designer key is too long. Fix to "Multiple Designer"')
            return False
        if ' and ' in content.get('designer', ''):
            logger.error('ER: Several designers in designer key. Fix to "Multiple Designer"')
            return False
        if ',' in content.get('designer', ''):
            logger.error('ER: Several designers in designer key. Fix to "Multiple Designer"')
            return False
        if '.' in content.get('designer', ''):
            logger.error('ER: Several designers in designer key. Fix to "Multiple Designer"')
            return False

        logger.info(u'OK: Designer "{}"'.format(content.get('designer', '')))
        return True

    def fix(self, check=True):
        if check:
            if not self.is_valid():
                return False
            return True

        if self.is_valid():
            logger.info(u'OK: Designer "{}"'.format(content.get('designer', '')))
            return True

        from bakery_cli.scripts.genmetadata import striplines
        content = {}
        with io.open(self.fontpath, 'r', encoding="utf-8") as fp:
            content = json.load(fp, object_pairs_hook=collections.OrderedDict)

        content['designer'] = 'Multiple Designers'
        with io.open(self.fontpath, 'w', encoding='utf-8') as f:
            contents = json.dumps(content, indent=2, ensure_ascii=False)
            f.write(striplines(contents))
        return True


class CreateDSIGFixer(Fixer):
    """ Create DSIG table in font if it does not exist """

    def get_shell_command(self):
        return "fontbakery-fix-dsig.py {}".format(self.fontpath)

    def fix(self):
        if 'DSIG' in self.font:
            return False

        try:
            from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
        except ImportError:
            error_message = ("The '{}' font does not have an existing"
                             " digital signature proving its authenticity,"
                             " so Fontbakery needs to add one. To do this"
                             " requires version 2.3 or later of Fonttools"
                             " to be installed. Please upgrade at"
                             " https://pypi.python.org/pypi/FontTools/2.4")
            logger.error(error_message.format(os.path.basename(self.fontpath)))
            return False


        newDSIG = ttLib.newTable("DSIG")
        newDSIG.ulVersion = 1
        newDSIG.usFlag = 1
        newDSIG.usNumSigs = 1
        sig = SignatureRecord()
        sig.ulLength = 20
        sig.cbSignature = 12
        sig.usReserved2 = 0
        sig.usReserved1 = 0
        sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
        sig.ulFormat = 1
        sig.ulOffset = 20
        newDSIG.signatureRecords = [sig]
        self.font.tables["DSIG"] = newDSIG
        return True


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


class NbspAndSpaceSameWidth(Fixer):

    def get_shell_command(self):
        return "fontbakery-fix-nbsp.py {}".format(self.fontpath)

    def getGlyph(self, uchar):
        for table in self.font['cmap'].tables:
            if not (table.platformID == 3 and table.platEncID in [1, 10]):
                continue
            if uchar in table.cmap:
                return table.cmap[uchar]
        return None

    def addCFFGlyph(self, glyphName=None, program=None, private=None,
          globalSubrs=None, charStringsIndex=None, topDict=None, charStrings=None):
        from fontTools.misc.psCharStrings import T2CharString
        charString = T2CharString(program=program, private=private, globalSubrs=globalSubrs)
        charStringsIndex.append(charString)
        glyphID = len(topDict.charset)
        charStrings.charStrings[glyphName] = glyphID
        topDict.charset.append(glyphName)

    def addGlyph(self, uchar, glyph):
        # Add to glyph list
        glyphOrder = self.font.getGlyphOrder()
        # assert glyph not in glyphOrder
        glyphOrder.append(glyph)
        self.font.setGlyphOrder(glyphOrder)

        # Add horizontal metrics (to zero)
        self.font['hmtx'][glyph] = [0, 0]

        # Add to cmap
        for table in self.font['cmap'].tables:
            if not (table.platformID == 3 and table.platEncID in [1, 10]):
                continue
            if not table.cmap:  # Skip UVS cmaps
                continue
            assert uchar not in table.cmap
            table.cmap[uchar] = glyph

        # Add empty glyph outline
        if 'glyf' in self.font:
            self.font['glyf'].glyphs[glyph] = ttLib.getTableModule('glyf').Glyph()
        else:
            cff = self.font['CFF '].cff
            self.addCFFGlyph(
                glyphName=glyph,
                private=cff.topDictIndex[0].Private,
                globalSubrs=cff.GlobalSubrs,
                charStringsIndex=cff.topDictIndex[0].CharStrings.charStringsIndex,
                # charStringsIndex=cff.topDictIndex[0].CharStrings.charStrings.charStringsIndex,
                topDict=cff.topDictIndex[0],
                charStrings=cff.topDictIndex[0].CharStrings
            )
            import ipdb; ipdb.set_trace()
        return glyph

    def getWidth(self, glyph):
        return self.font['hmtx'][glyph][0]

    def setWidth(self, glyph, width):
        self.font['hmtx'][glyph] = (width, self.font['hmtx'][glyph][1])

    def glyphHasInk(self, name):
        """Checks if specified glyph has any ink.
        That is, that it has at least one defined contour associated. Composites are
        considered to have ink if any of their components have ink.
        Args:
            glyph_name: The name of the glyph to check for ink.
        Returns:
            True if the font has at least one contour associated with it.
        """
        glyph = self.font['glyf'].glyphs[name]
        glyph.expand(self.font['glyf'])

        if not glyph.isComposite():
            if glyph.numberOfContours == 0:
                return False
            (coords, _, _) = glyph.getCoordinates(self.font['glyf'])
            # you need at least 3 points to draw
            return len(coords) > 2

        # composite is blank if composed of blanks
        # if you setup a font with cycles you are just a bad person
        for glyph_name in glyph.getComponentNames(glyph.components):
            if self.glyphHasInk(glyph_name):
                return True

        return False

    def fix(self, check=False):
        retval = False
        fontfile = os.path.basename(self.fontpath)

        space = self.getGlyph(0x0020)
        if space != None and space not in ["space", "uni0020"]:
            logger.error('ER: {}: Glyph 0x0020 is called "{}": Change to "space" or "uni0020"'.format(fontfile, space))

        nbsp = self.getGlyph(0x00A0)
        if nbsp != None and nbsp not in ["nbsp", "uni00A0", "nonbreakingspace", "nbspace"]:
            logger.error('ER: {}: Glyph 0x00A0 is called "{}": Change to "nbsp" or "uni00A0"'.format(fontfile, nbsp))

        isNbspAdded = isSpaceAdded = False
        if not nbsp:
            isNbspAdded = True
            try:
                nbsp = self.addGlyph(0x00A0, 'nbsp')
            except Exception as ex:
                logger.error('ER: {}'.format(ex))
                return False
        if not space:
            isSpaceAdded = True
            try:
                space = self.addGlyph(0x0020, 'space')
            except Exception as ex:
                logger.error('ER: {}'.format(ex))
                return False

        for g in [space, nbsp]:
            if self.glyphHasInk(g):
                if check:
                    logger.error('ER: {}: Glyph "{}" has ink. Delete any contours or components'.format(fontfile, g))
                else:
                    logger.error('OK: {}: Glyph "{}" has ink. Fixed: Overwritten by an empty glyph'.format(fontfile, g))
                    #overwrite existing glyph with an empty one
                    self.font['glyf'].glyphs[g] = ttLib.getTableModule('glyf').Glyph()
                    retval = True

        spaceWidth = self.getWidth(space)
        nbspWidth = self.getWidth(nbsp)

        if spaceWidth != nbspWidth or nbspWidth < 0:

            self.setWidth(nbsp, min(nbspWidth, spaceWidth))
            self.setWidth(space, min(nbspWidth, spaceWidth))

            if isNbspAdded:
                if check:
                    msg = 'ER: {} space {} nbsp None: Add nbsp with advanceWidth {}'
                else:
                    msg = 'OK: {} space {} nbsp None: Added nbsp with advanceWidth {}'
                logger.error(msg.format(fontfile, spaceWidth, spaceWidth))

            if isSpaceAdded:
                if check:
                    msg = 'ER: {} space None nbsp {}: Add space with advanceWidth {}'
                else:
                    msg = 'OK: {} space None nbsp {}: Added space with advanceWidth {}'
                logger.error(msg.format(fontfile, nbspWidth, nbspWidth))
                
            if nbspWidth > spaceWidth and spaceWidth >= 0:
                if check:
                    msg = 'ER: {} space {} nbsp {}: Change space advanceWidth to {}'
                else:
                    msg = 'OK: {} space {} nbsp {}: Fixed space advanceWidth to {}'
                logger.error(msg.format(fontfile, spaceWidth, nbspWidth, nbspWidth))
            else:
                if check:
                    msg = 'ER: {} space {} nbsp {}: Change nbsp advanceWidth to {}'
                else:
                    msg = 'OK: {} space {} nbsp {}: Fixed nbsp advanceWidth to {}'
                logger.error(msg.format(fontfile, spaceWidth, nbspWidth, spaceWidth))
            return True

        logger.info('OK: {} space {} nbsp {}'.format(fontfile, spaceWidth, nbspWidth))
        return retval


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


def fontTools_to_dict(font):
    fontdata = {
        'names': [
            {'nameID': rec.nameID,
             'platformID': rec.platformID,
             'langID': rec.langID,
             'string': rec.string.decode("utf_16_be")
             if rec.isUnicode() else rec.string,
             'platEncID': rec.platEncID} for rec in font['name'].names
        ],
        'OS/2': {
            'fsSelection': font['OS/2'].fsSelection,
            'usWeightClass': font['OS/2'].usWeightClass,
        },
        'head': {
            'macStyle': font['head'].macStyle,
        },
        'post': {
            'italicAngle': font['post'].italicAngle
        }
    }
    if 'CFF ' in font:
        fontdata['CFF'] = {
            'Weight': font['CFF '].cff.topDictIndex[0].Weight
        }
    return fontdata


class StyleNameRecommendationFixer(Fixer):
    def fix(self):
        fontfile = os.path.basename(self.fontpath)
        font = Font(ttfont=self.font)

        if font.stylename in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
            font.ot_style_name = font.stylename
            logger.error('OK: {}: Fixed: Windows-only Opentype-specific StyleName set'
                         ' to "{}".'.format(fontfile, font.stylename))
        else:
            logger.error('OK: {}: Warning: Windows-only Opentype-specific StyleName set to "Regular"'
                         ' as a default value. Please verify if this is correct.'.format(fontfile))
            font.ot_style_name = 'Regular'

        logger.error('OK: {}: Fixed: Windows-only Opentype-specific FamilyName set to "{}"'.format(fontfile, font.familyname))
        return True


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


class FamilyAndStyleNameFixer(Fixer):

    def get_shell_command(self):
        return "fontbakery-fix-opentype-names.py {}".format(self.fontpath)

    def getOrCreateNameRecord(self, nameId, val):
        if nameId < 10:
            nameId = " " + str(nameId)

        logger.error('NAMEID {}: "{}"'.format(nameId, val))
        return

        result_namerec = None
        for k, p in [[1, 0], [3, 1]]:
            result_namerec = self.font['name'].getName(nameId, k, p)
            if result_namerec:
                result_namerec.string = (val or '').encode(result_namerec.getEncoding())
                
        if result_namerec:
            return result_namerec

        ot_namerecord = NameRecord()
        ot_namerecord.nameID = nameId
        ot_namerecord.platformID = 3
        ot_namerecord.langID = 0x409
        # When building a Unicode font for Windows, the platform ID
        # should be 3 and the encoding ID should be 1
        ot_namerecord.platEncID = 1
        ot_namerecord.string = (val or '').encode(ot_namerecord.getEncoding())

        self.font['name'].names.append(ot_namerecord)
        return ot_namerecord


    def fix(self):
        # Convert huge and complex fontTools to config python dict
        fontdata = fontTools_to_dict(self.font)

        fontdata = clean_name_values(fontdata)
        familyname = ''
        for rec in fontdata['names']:
            if rec['nameID'] == NAMEID_FONT_FAMILY_NAME:
                familyname = rec['string']
                break
        fontdata = fix_all_names(fontdata, familyname)

        logger.error(os.path.basename(self.fontpath))
        logger.error('')
        for field in fontdata['names']:
            self.getOrCreateNameRecord(field['nameID'], field['string'])
        return True


class RemoveNameRecordWithOpyright(Fixer):

    def containsSubstr(self, namerecord, substr):
        string = namerecord.string.decode(namerecord.getEncoding())
        return bool(substr in string)

    def fix(self):
        records = []
        for record in self.font['name'].names:
            if self.containsSubstr(record, 'opyright') and record.nameID == NAMEID_DESCRIPTION:
                continue
            records.append(record)
        self.font['name'].names = records
        return True


class RemoveItemsWithPlatformID1(Fixer):

    def fix(self):
        records = []
        for record in self.font['name'].names:
            if record.platformID == 1:
                continue
            records.append(record)
        self.font['name'].names = records
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


class RenameFileWithSuggestedName(Fixer):

    def validate(self):
        sugested = getSuggestedFontNameValues(self.font)
        family_name = sugested['family']
        subfamily_name = sugested['subfamily']
        expectedname = '{0}-{1}'.format(family_name.replace(' ', ''),
                                        subfamily_name.replace(' ', ''))
        actualname, extension = os.path.splitext(self.fontpath)

        return '{0}{1}'.format(expectedname, extension)

    def fix(self):
        newfilename = self.validate()

        new_targetpath = os.path.join(os.path.dirname(self.fontpath),
                                      newfilename)
        shutil.move(self.fontpath, new_targetpath)

        from bakery_cli.logger import logger
        logger.error('$ mv {} {}'.format(self.fontpath, os.path.basename(new_targetpath)))

        self.testcase.operator.path = new_targetpath
        from bakery_cli.utils import ProcessedFile
        
        f = ProcessedFile()
        f.filepath = newfilename

        self.save_after_fix = False
        return True


class SpaceIndentationWriter(Fixer):

    def loadfont(self, path):
        return  # this fixer does not operate with font

    def apply(self, *args, **kwargs):
        string = ''
        for line in open(self.fontpath):
            string += line.expandtabs(2)
        fp = open(self.fontpath, 'w')
        fp.write(string)
        return True
