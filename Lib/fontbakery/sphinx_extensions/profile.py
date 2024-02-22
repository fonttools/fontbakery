from typing import Any

from sphinx.ext.autodoc import ModuleDocumenter
from sphinx.application import Sphinx

from fontbakery.fonts_profile import load_all_checks, checks_by_id


def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension
    app.add_autodocumenter(FontbakeryProfileDocumenter)
    load_all_checks()


class FontbakeryProfileDocumenter(ModuleDocumenter):
    objtype = "profile"
    directivetype = ModuleDocumenter.objtype
    priority = 10 + ModuleDocumenter.priority

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return hasattr(member, "PROFILE")

    def add_content(
        self,
        more_content: Any | None,
        # no_docstring: bool = False,
    ) -> None:
        super().add_content(more_content)
        source_name = self.get_sourcename()
        profile = self.object
        overrides = profile.PROFILE.get("overrides", {})
        defaults = profile.PROFILE.get("configuration_defaults", {})
        if "include_profiles" in profile.PROFILE:
            # This could be a link
            included = [
                f":doc:`{profile}`" for profile in profile.PROFILE["include_profiles"]
            ]
            self.add_line("Included profiles: " + ", ".join(included), source_name)
            self.add_line("", source_name)
        for section, checks in profile.PROFILE["sections"].items():
            self.add_line(f"{section}", source_name)
            for check in checks:
                if check in checks_by_id:
                    self.add_line(
                        f"  - *{check}*: {checks_by_id[check].description}", source_name
                    )
                else:
                    self.add_line(f"  - *{check}*", source_name)
                if check in overrides:
                    self.add_line("", source_name)
                    for override in overrides[check]:
                        code, status, reason = (
                            override["code"],
                            override["status"],
                            override.get("reason"),
                        )
                        self.add_line(
                            f"    - The **{code}** result is reported as a"
                            " **{status}** in this profile",
                            source_name,
                        )
                        if reason:
                            self.add_line("", source_name)
                            self.add_line(f"      {reason}", source_name)
                        self.add_line("", source_name)
                if check in defaults:
                    self.add_line("", source_name)
                    self.add_line(
                        "    - For this check, the following parameters are configured:",
                        source_name,
                    )
                    self.add_line("", source_name)
                    for param, value in defaults[check].items():
                        self.add_line(f"      - ``{param}``: ``{value}``", source_name)
                    self.add_line("", source_name)
