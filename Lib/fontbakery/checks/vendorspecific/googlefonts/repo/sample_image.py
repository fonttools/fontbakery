import glob
import os
import re

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import bullet_list


@check(
    id="googlefonts/repo/sample_image",
    rationale="""
        In order to showcase what a font family looks like, the project's README.md
        file should ideally include a sample image and highlight it in the upper
        portion of the document, no more than 10 lines away from the top of the file.
    """,
    conditions=["readme_contents", "readme_directory"],
    proposal="https://github.com/fonttools/fontbakery/issues/2898",
)
def check_repo_sample_image(readme_contents, readme_directory, config):
    """Check README.md has a sample image."""

    image_path = False
    line_number = 0
    for line in readme_contents.split("\n"):
        if line.strip() == "":
            continue

        line_number += 1
        # We're looking for something like this:
        # ![Raleway font sample](documents/raleway-promo.jpg)
        # And we accept both png and jpg files
        result = re.match(r"\!\[.*\]\((.*\.(png|jpg))\)", line)
        if result:
            image_path = os.path.join(readme_directory, result[1].replace("/", os.sep))
            break

    local_image_files = glob.glob(os.path.join(readme_directory, "**/*.[jp][np]g"))

    if local_image_files:
        sample_tip = local_image_files[0]
    else:
        sample_tip = "samples/some-sample-image.jpg"
    MARKDOWN_IMAGE_SYNTAX_TIP = (
        f"You can use something like this:\n\n" f"\t![font sample]({sample_tip})"
    )

    if image_path:
        if image_path not in local_image_files:
            yield FAIL, Message(
                "image-missing",
                f"The referenced sample image could not be found:"
                f" {os.path.join(readme_directory, image_path)}\n",
            )
        else:
            if line_number >= 10:
                yield WARN, Message(
                    "not-ideal-placement",
                    "Please consider placing the sample image closer"
                    " to the top of the README document so that it is"
                    " more immediately viewed by readers.\n",
                )
    else:  # if no image reference was found on README.md:
        if local_image_files:
            yield WARN, Message(
                "image-not-displayed",
                f"Even though the README.md file does not display"
                f" a font sample image, a few image files were found:\n\n"
                f"{bullet_list(config, local_image_files)}\n"
                f"\n"
                f"Please consider including one of those images on the README.\n"
                f"{MARKDOWN_IMAGE_SYNTAX_TIP}\n",
            )
        else:
            yield WARN, Message(
                "no-sample",
                f"Please add a font sample image to the README.md file.\n"
                f"{MARKDOWN_IMAGE_SYNTAX_TIP}\n",
            )
