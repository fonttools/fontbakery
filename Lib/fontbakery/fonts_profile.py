"""
Font Bakery CheckRunner is the driver of a font bakery suite of checks.
"""
import glob
import logging
import argparse
from dataclasses import dataclass

from fontbakery.callable import FontBakeryExpectedValue as ExpectedValue
from fontbakery.profile import Profile
from fontbakery.errors import ValueValidationError


@dataclass
class FileDescription:
    name: str
    extensions: list
    singular: str
    description: str


class FontsProfile(Profile):
    accepted_files = [
        FileDescription(name="fonts",
                        singular="font",
                        extensions=[".otf",".ttf"],
                        description="OpenType binary"),
        FileDescription(name="ufos",
                        singular="ufo",
                        extensions=[".ufo"],
                        description="UFO source"),
        FileDescription(name="designspaces",
                        singular="designspace",
                        extensions=[".designspace"],
                        description="Designspace"),
        FileDescription(name="glyphs_files",
                        singular="glyphs_file",
                        extensions=[".glyphs"],
                        description="Glyphs source"),
        FileDescription(name="readme_md",
                        singular="readme_md",
                        extensions=["README.md"],
                        description="Project's README markdown file"),
        FileDescription(name="metadata_pb",
                        singular="metadata_pb",
                        extensions=["METADATA.pb"],
                        description="Project's METADATA protobuf file"),
    ]

    def setup_argparse(self, argument_parser):
        """
        Set up custom arguments needed for this profile.
        """
        profile = self

        def get_files(pattern):
            files_to_check = []
            # use glob.glob to accept *.ttf
            # but perform a hacky fixup to workaround the square-brackets naming scheme
            # currently in use for varfonts in google fonts...
            if '].ttf' in pattern:
                pattern = "*.ttf".join(pattern.split('].ttf'))

            # Everything goes in for now, gets sorted in the Merge
            for fullpath in glob.glob(pattern):
                files_to_check.append(fullpath)
            return files_to_check


        class MergeAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                for file_description in profile.accepted_files:
                    setattr(namespace, file_description.name, [])
                target = [item for l in values for item in l]
                any_accepted = False
                for file in target:
                    accepted = False
                    for file_description in profile.accepted_files:
                        if any([file.endswith(extension) for extension in file_description.extensions]):
                          setattr(namespace, file_description.name, getattr(namespace, file_description.name) + [file])
                          accepted = True
                          any_accepted = True
                    if not accepted:
                        logging.info(f"Skipping '{file}' as it does not"
                                     f" seem to be accepted by this profile.")
                if not any_accepted:
                    raise ValueValidationError('No applicable files found')

        argument_parser.add_argument(
            'files',
            # To allow optional commands like "-L" to work without other input
            # files:
            nargs='*',
            type=get_files,
            action=MergeAction,
            help='file path(s) to check. Wildcards like *.ttf are allowed.')

        return tuple(x.name for x in self.accepted_files)

    def get_family_checks(self):
        family_checks = self.get_checks_by_dependencies('fonts')
        family_checks.extend(self.get_checks_by_dependencies('ttFonts'))
        return family_checks

    @classmethod
    def _expected_values(cls):
        return { val.name:
          ExpectedValue(val.name,
                        default = [],
                        description = f"A list of the {val.description} file paths to check",
                        force=True
                        )
          for val in cls.accepted_files
        }

    @classmethod
    def _iterargs(cls):
        return { val.singular: val.name for val in cls.accepted_files }


def profile_factory(**kwds):
    from fontbakery.profiles.shared_conditions import ttFont
    profile = FontsProfile(
        iterargs=FontsProfile._iterargs()
      , conditions={ttFont.name: ttFont}
      , derived_iterables={'ttFonts': ('ttFont', True)}
      , expected_values=FontsProfile._expected_values()
      , **kwds
    )
    return profile
