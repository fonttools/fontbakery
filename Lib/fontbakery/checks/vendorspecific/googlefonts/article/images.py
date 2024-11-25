import os

from fontbakery.prelude import check, Message, FATAL, FAIL, WARN, PASS


@check(
    id="googlefonts/article/images",
    conditions=["family_directory"],
    rationale="""
        The purpose of this check is to ensure images (either raster or vector files)
        are not excessively large in filesize and resolution.

        These constraints are loosely based on infrastructure limitations under
        default configurations.

        It also ensures that the article page has a minimum length and includes
        at least one visual asset.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4594",
)
def check_article_images(config, family_directory):
    """Validate size, and resolution of article images,
    and ensure article page has minimum length and includes visual assets."""
    from bs4 import BeautifulSoup
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
    article_path = os.path.join(article_dir, "ARTICLE.en_us.html")

    if not os.path.exists(article_path):
        yield WARN, Message(
            "lacks-article",
            f"Family metadata at {family_directory} does not have an article.\n",
        )
        return

    with open(article_path, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()
    word_count = len(text.split())
    char_count = len(text)

    visuals = soup.find_all(["img", "svg", "video", "iframe"])
    missing_files = []
    for visual in visuals:
        if src := visual.get("src"):
            visual_path = os.path.join(article_dir, src)
            if not os.path.exists(visual_path):
                missing_files.append(src)

    if word_count < 100 or char_count < 500:
        yield WARN, Message(
            "length-requirements-not-met",
            "Article page is too short!",
        )

    if not visuals:
        yield WARN, Message("missing-visual-asset", "Article page lacks visual assets.")

    if missing_files:
        yield FATAL, Message(
            "missing-visual-file",
            f"Visual asset files are missing:\n{bullet_list(config, missing_files)}",
        )

    all_image_files = [
        os.path.join(article_dir, filename)
        for filename in os.listdir(article_dir)
        if is_vector(filename) or is_raster(filename)
    ]

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
                f"Max resolution allowed: `{MAX_WIDTH} x {MAX_HEIGHT} pixels`",
            )

    yield PASS, "ok"
