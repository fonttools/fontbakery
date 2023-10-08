"""
FontBakery CheckRunner is the driver of a fontbakery suite of checks.
"""
import glob
import logging
import argparse
from dataclasses import dataclass
import os

from fontbakery.callable import (
    FontBakeryExpectedValue as ExpectedValue,
)
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
        FileDescription(
            name="fonts",
            singular="font",
            extensions=[".otf", ".ttf"],
            description="OpenType binary",
        ),
        FileDescription(
            name="ufos", singular="ufo", extensions=[".ufo"], description="UFO source"
        ),
        FileDescription(
            name="designspaces",
            singular="designspace",
            extensions=[".designspace"],
            description="Designspace",
        ),
        FileDescription(
            name="glyphs_files",
            singular="glyphs_file",
            extensions=[".glyphs"],
            description="Glyphs source",
        ),
        FileDescription(
            name="readme_md",
            singular="readme_md",
            extensions=["README.md"],
            description="Project's README markdown file",
        ),
        FileDescription(
            name="metadata_pb",
            singular="metadata_pb",
            extensions=["METADATA.pb"],
            description="Project's METADATA protobuf file",
        ),
    ]

    def setup_argparse(self, argument_parser):
        """
        Set up custom arguments needed for this profile.
        """
        profile = self

        def get_files(pattern):
            if os.path.exists(pattern):
                # not a pattern
                return [pattern]
            files_to_check = []
            # use glob.glob to accept *.ttf
            # Everything goes in for now, gets sorted in the Merge
            for fullpath in glob.glob(pattern):
                files_to_check.append(fullpath)
            return files_to_check

        class MergeAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                if namespace.list_checks:
                    # -L/--list-checks option was used; don't try to validate file
                    # inputs because this option doesn't require them
                    return
                for file_description in profile.accepted_files:
                    setattr(namespace, file_description.name, [])
                # flatten the 'values' list: [['a'], ['b']] => ['a', 'b']
                target = [item for sublist in values for item in sublist]
                any_accepted = False
                for file in target:
                    accepted = False
                    for file_description in profile.accepted_files:
                        if any(
                            [
                                file.endswith(extension)
                                for extension in file_description.extensions
                            ]
                        ):
                            setattr(
                                namespace,
                                file_description.name,
                                getattr(namespace, file_description.name) + [file],
                            )
                            accepted = True
                            any_accepted = True
                    if not accepted:
                        logging.info(
                            "Skipping '{}' as it does not"
                            " seem to be accepted by this profile.",
                            file,
                        )
                if not any_accepted:
                    raise ValueValidationError("No applicable files found")

        argument_parser.add_argument(
            "files",
            nargs="*",  # allow no input files; needed for -L/--list-checks option
            type=get_files,
            action=MergeAction,
            help="file path(s) to check. Wildcards like *.ttf are allowed.",
        )

        return tuple(x.name for x in self.accepted_files)

    def get_family_checks(self):
        family_checks = self.get_checks_by_dependencies("fonts")
        family_checks.extend(self.get_checks_by_dependencies("ttFonts"))
        return family_checks

    @classmethod
    def _expected_values(cls):
        return {
            val.name: ExpectedValue(
                val.name,
                default=[],
                description=f"A list of the {val.description} file paths to check",
                force=True,
            )
            for val in cls.accepted_files
        }

    @classmethod
    def _iterargs(cls):
        return {val.singular: val.name for val in cls.accepted_files}


def profile_factory(**kwds):
    profile = FontsProfile(
        iterargs=FontsProfile._iterargs(),
        derived_iterables={"ttFonts": ("ttFont", True)},
        expected_values=FontsProfile._expected_values(),
        **kwds,
    )
    return profile
