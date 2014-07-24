from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata


class CheckMetadataFields(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    @tags('required')
    def test_check_metadata_fields(self):
        """ Check METADATA.json "fonts" property items have required field """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        keys = [("name", str), ("postScriptName", str),
                ("fullName", str), ("style", str),
                ("weight", int), ("filename", str),
                ("copyright", str)]

        missing = set([])
        unknown = set([])

        for j, itemtype in keys:

            for font_metadata in family.fonts:
                if j not in font_metadata:
                    missing.add(j)

                for k in font_metadata:
                    if k not in map(lambda x: x[0], keys):
                        unknown.add(k)

        if unknown:
            msg = 'METADATA.json "fonts" property has unknown items [%s]'
            self.fail(msg % ', '.join(unknown))

        if missing:
            msg = 'METADATA.json "fonts" property items missed [%s] items'
            self.fail(msg % ', '.join(missing))

