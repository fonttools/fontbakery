from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckGposTableHasKerningInfo(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_gpos_table_has_kerning_info(self):
        """ GPOS table has kerning information """
        font = Font.get_ttfont(self.path)

        try:
            font['GPOS']
        except KeyError:
            self.fail('"GPOS" does not exist in font')
        flaglookup = False
        for lookup in font['GPOS'].table.LookupList.Lookup:
            if lookup.LookupType == 2:  # Adjust position of a pair of glyphs
                flaglookup = lookup
                break  # break for..loop to avoid reading all kerning info
        self.assertTrue(flaglookup, msg='GPOS doesnt have kerning information')
        self.assertGreater(flaglookup.SubTableCount, 0)
        self.assertGreater(flaglookup.SubTable[0].PairSetCount, 0)
