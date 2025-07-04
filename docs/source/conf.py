# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../Lib"))


# -- Project information -----------------------------------------------------

project = "Font Bakery"
copyright = "2025 The Font Bakery Authors"
author = "The Font Bakery Authors"

# The short X.Y version
version = "1.0"
# The full version, including alpha/beta/rc tags
release = "1.0.1"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "4.3"

# Add any Sphinx extension module names here, as strings.
# They can be extensions coming with Sphinx (named 'sphinx.ext.*')
# or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.linkcode",
    "fontbakery.sphinx_extensions.profile",
    "sphinx.ext.napoleon",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst", ".md"]

# The main toctree document.
main_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {"display_version": False}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "FontBakerydoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        main_doc,
        "FontBakery.tex",
        "Font Bakery Documentation",
        "The Font Bakery Authors",
        "manual",
    )
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(main_doc, "fontbakery", "Font Bakery Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        main_doc,
        "FontBakery",
        "Font Bakery Documentation",
        author,
        "FontBakery",
        "Well designed Font QA tool, written in Python 3.",
        "Miscellaneous",
    )
]


# -- Extension configuration -------------------------------------------------


def linkcode_resolve(domain, info):
    # hmmm: related https://github.com/sphinx-doc/sphinx/issues/1556
    # ipdb> info
    # {'module': 'fontbakery.callable', 'fullname': 'Disabled'}
    # ipdb> domain
    # 'py'

    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")

    # We must get the "tree" part dynamically, best would be the release
    # tag, if it is the same as the version that we are building at the
    # moment. Second best probably a hash. The branch HEAD is only of
    # limited usefulnes as the documentation will become out of sync.
    #
    # On GitHub, we can link to a tag i.e. a release tag such as "v0.7.2"
    # as seen on this URL:
    # https://github.com/fonttools/fontbakery/tree/v0.7.2/Lib/fontbakery/profiles

    tree = release
    # It's not planned for us to get the line number :-(
    # I had to hammer this data into the info.
    if "lineno" in info:
        lineno = "#L{}".format(info["lineno"])
    else:
        lineno = ""

    return "https://github.com/fonttools/fontbakery/tree/{}/Lib/{}.py{}".format(
        tree, filename, lineno
    )
