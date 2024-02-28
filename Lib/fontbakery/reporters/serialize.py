"""
FontBakery reporters/serialize can report the events of the FontBakery
CheckRunner Protocol to a serializeable document e.g. for usage with `json.dumps`.

Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from fontbakery.result import CheckResult
from fontbakery.reporters import FontbakeryReporter


class SerializeReporter(FontbakeryReporter):
    format = "unknown"

    def __post_init__(self):
        super().__post_init__()
        self._doc = None
        self._sections = {}

        # used when self.collect_results_by is set
        # this way we minimize our knowledge of the profile
        self._max_cluster_by_index = None
        self._observed_checks = {}

    def start(self, order):
        super().start(order)
        self._sections = {}

    def receive_result(self, checkresult: CheckResult):
        super().receive_result(checkresult)
        section = checkresult.identity.section
        if section.name not in self._sections:
            self._sections[section.name] = {
                "checks": [],
                "key": [section.name, None, None],
            }
        self._sections[section.name]["checks"].append(checkresult.getData(self.runner))

    def end(self):
        super().end()
        for section in self._sections.keys():
            self._sections[section]["result"] = self._sectioncounter[section]

    def getdoc(self):
        return {
            "result": self._counter,
            "sections": list(self._sections.values()),
        }

    def write(self):
        with open(self.output_file, "w", encoding="utf-8") as fh:
            fh.write(self.template(self.getdoc()))
        if not self.quiet:
            print(
                f'A report in {self.format} format has been saved to "{self.output_file}"'
            )

    def template(self, _data):
        raise NotImplementedError(
            "Subclasses of SerializeReporter must implement the template method"
        )


class JSONReporter(SerializeReporter):
    format = "JSON"

    def template(self, doc):
        import json

        return json.dumps(doc, sort_keys=True, indent=4)
