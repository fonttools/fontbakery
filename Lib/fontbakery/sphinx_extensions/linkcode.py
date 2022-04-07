"""
    sphinx.ext.linkcode
    ~~~~~~~~~~~~~~~~~~~

    Add external links to module code in Python object descriptions.

    :copyright: Copyright 2007-2019 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# started as a clone of
# https://github.com/sphinx-doc/sphinx/blob/f4a98d8ca0cc88a5a993a6b90a3af0892fdc19c0/sphinx/ext/linkcode.py

from docutils import nodes

import sphinx
from sphinx import addnodes
from sphinx.errors import SphinxError
from sphinx.locale import _

if False:  # pylint: disable=using-constant-test
    # For type annotation
    from typing import Any, Dict, Set  # NOQA
    from sphinx.application import Sphinx  # NOQA


class LinkcodeError(SphinxError):
    category = "linkcode error"


def doctree_read(app, doctree):
    # type: (Sphinx, nodes.Node) -> None
    env = app.builder.env

    resolve_target = getattr(env.config, "linkcode_resolve", None)
    if not callable(env.config.linkcode_resolve):
        raise LinkcodeError("Function `linkcode_resolve` is not given in conf.py")

    domain_keys = {
        "py": ["module", "fullname"],
        "c": ["names"],
        "cpp": ["names"],
        "js": ["object", "fullname"],
    }

    for objnode in doctree.traverse(addnodes.desc):
        domain = objnode.get("domain")
        uris = set()  # type: Set[str]
        for signode in objnode:
            if not isinstance(signode, addnodes.desc_signature):
                continue

            # Convert signode to a specified format
            info = {}
            for key in domain_keys.get(domain, []):
                value = signode.get(key)
                if not value:
                    value = ""
                info[key] = value
            if not info:
                continue

            if "lineno" in signode.attributes:
                info["lineno"] = signode.attributes["lineno"]
            # Call user code to resolve the link
            uri = resolve_target(domain, info)
            if not uri:
                # no source
                continue

            if uri in uris or not uri:
                # only one link per name, please
                continue
            uris.add(uri)

            inline = nodes.inline("", _("[source]"), classes=["viewcode-link"])
            onlynode = addnodes.only(expr="html")
            onlynode += nodes.reference("", "", inline, internal=False, refuri=uri)
            signode += onlynode


def setup(app):
    # type: (Sphinx) -> Dict[str, Any]
    app.connect("doctree-read", doctree_read)
    app.add_config_value("linkcode_resolve", None, "")
    return {"version": sphinx.__display_version__, "parallel_read_safe": True}
