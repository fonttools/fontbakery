import os

from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="com.google.fonts/check/article/images",
    conditions=["family_directory"],
    rationale="""
        The purpose of this check is to ensure images (either raster or vector files)
        are placed on the correct directory (an `images` subdirectory inside `article`) and
        they they are not excessively large in filesize and resolution.

        These constraints are loosely based on infrastructure limitations under
        default configurations.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4594",
    experimental="Since 2024/Mar/25",
)
def com_google_fonts_check_metadata_parses(config, family_directory):
    """Validate location, size and resolution of article images."""

    from fontbakery.utils import bullet_list, image_dimensions

    MAX_WIDTH = 2048
    MAX_HEIGHT = 1024
    MAXSIZE_VECTOR = 1750 * 1024  # 1750kb
    MAXSIZE_RASTER = 800 * 1024  # 800kb

    def is_raster(filename):
        for ext in ["png", "jpg", "jpeg", "jxl", "gif"]:
            if filename.lower().endswith(f".{ext}"):
                return True
        return False

    def is_vector(filename):
        for ext in ["svg"]:
            if filename.lower().endswith(f".{ext}"):
                return True
        return False

    article_dir = os.path.join(family_directory, "article")
    images_dir = os.path.join(family_directory, "article", "images")
    if not os.path.isdir(article_dir):
        yield WARN, Message(
            "lacks-article",
            f"Family metadata at {family_directory} does not have an article.\n",
        )
    else:
        misplaced_files = [
            os.path.join(article_dir, filename)
            for filename in os.listdir(article_dir)
            if is_vector(filename) or is_raster(filename)
        ]
        all_image_files = misplaced_files
        if os.path.isdir(images_dir):
            all_image_files += [
                os.path.join(images_dir, filename)
                for filename in os.listdir(images_dir)
                if is_vector(filename) or is_raster(filename)
            ]
        if misplaced_files:
            yield WARN, Message(
                "misplaced-image-files",
                f"There are {len(misplaced_files)} image files in the `article`"
                f" directory and they should be moved to an `article/images`"
                f" subdirectory:\n\n"
                f"{bullet_list(config, misplaced_files)}\n",
            )

        for filename in all_image_files:
            if is_vector(filename):
                maxsize = MAXSIZE_VECTOR
                imagetype = "vector"
            elif is_raster(filename):
                maxsize = MAXSIZE_RASTER
                imagetype = "raster"
            else:
                # ignore this file type
                continue

            filesize = os.stat(filename).st_size
            if filesize > maxsize:
                yield FAIL, Message(
                    "filesize",
                    f"`{filename}` has `{filesize} bytes`, but the maximum filesize"
                    f" for {imagetype} images is `{maxsize} bytes`.",
                )

            dim = image_dimensions(filename)
            if dim is None:
                # Could not detect image dimensions
                continue

            w, h = dim
            if w > MAX_WIDTH or h > MAX_HEIGHT:
                yield FAIL, Message(
                    "image-too-large",
                    f"Image is too large: `{w} x {h} pixels`\n\n"
                    f"Max resulution allowed: `{MAX_WIDTH} x {MAX_HEIGHT} pixels`",
                )
