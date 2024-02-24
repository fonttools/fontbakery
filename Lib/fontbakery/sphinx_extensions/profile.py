from typing import Any, Optional

import m2r
from sphinx.application import Sphinx
from sphinx.ext.autodoc import FunctionDocumenter, ModuleDocumenter

from fontbakery.callable import FontBakeryCheck
from fontbakery.fonts_profile import checks_by_id, load_all_checks
from fontbakery.utils import unindent_and_unwrap_rationale


def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension
    app.add_autodocumenter(FontbakeryProfileDocumenter)
    app.add_autodocumenter(FontbakeryCheckDocumenter)
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
        more_content: Optional[Any],
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
                        f"  - :ref:`{check}`: {checks_by_id[check].description}",
                        source_name,
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
                            f" **{status}** in this profile",
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


class FontbakeryCheckDocumenter(FunctionDocumenter):
    objtype = "function"
    directivetype = FunctionDocumenter.objtype
    priority = 10 + FunctionDocumenter.priority

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        return isinstance(member, FontBakeryCheck)

    def add_content(
        self,
        more_content: Optional[Any],
        # no_docstring: bool = False,
    ) -> None:
        source_name = self.get_sourcename()
        check = self.object
        self.add_line("*" + check.description + "*", source_name)
        self.add_line("", source_name)
        for section in ["rationale", "proposal", "proponent", "conditions", "severity"]:
            if getattr(check, section):
                getattr(self, f"render_{section}")()
        self.add_line("", source_name)

    def render_rationale(self) -> None:
        check = self.object
        source_name = self.get_sourcename()
        for line in m2r.convert(unindent_and_unwrap_rationale(check.rationale)).split(
            "\n"
        ):
            self.add_line("  " + line, source_name)

    def render_proposal(self) -> None:
        check = self.object
        source_name = self.get_sourcename()
        self.add_line("", source_name)
        if isinstance(check.proposal, list):
            for ix, proposal in enumerate(check.proposal):
                if ix == 0:
                    self.add_line(f"* **Original proposal**: {proposal}", source_name)
                else:
                    self.add_line(
                        f"* **Some additional changes were proposed at** {proposal}",
                        source_name,
                    )
        else:
            self.add_line(f"* **Original proposal**: {check.proposal}", source_name)

    def render_proponent(self):
        check = self.object
        source_name = self.get_sourcename()
        self.add_line("", source_name)
        self.add_line(f"**Proponent**: {check.proponent}", source_name)

    def render_conditions(self):
        check = self.object
        source_name = self.get_sourcename()
        self.add_line("", source_name)
        conditions = ", ".join([f"``{cond}``" for cond in check.conditions])
        self.add_line(f"* **Conditions**: {conditions}", source_name)

    def render_severity(self):
        check = self.object
        source_name = self.get_sourcename()
        self.add_line("", source_name)
        self.add_line(f"* **Severity**: {check.severity}", source_name)

    def get_sourcename(self) -> str:
        return self.object.id

    def add_directive_header(self, sig: str) -> None:
        """Add the directive header and options to the generated content."""
        domain = getattr(self, "domain", "py")
        directive = getattr(self, "directivetype", self.objtype)
        name = self.format_name()
        sourcename = self.get_sourcename()

        self.add_line(".. _" + self.object.id + ":", sourcename)
        self.add_line("", sourcename)

        self.add_line(self.object.id, sourcename)
        self.add_line("^" * len(self.object.id), sourcename)

        # one signature per line, indented by column
        prefix = f".. {domain}:{directive}:: "
        for i, sig_line in enumerate(sig.split("\n")):
            self.add_line(f"{prefix}{name}{sig_line}", sourcename)
            if i == 0:
                prefix = " " * len(prefix)
