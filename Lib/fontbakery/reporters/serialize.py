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
from fontbakery.events import Identity
from fontbakery.status import Status, DEBUG, END, ENDCHECK, SECTIONSUMMARY, START
from fontbakery.reporters import FontbakeryReporter


class SerializeReporter(FontbakeryReporter):
    """
    usage:
    >> sr = SerializeReporter(runner=runner, collect_results_by='font')
    >> sr.run()
    >> import json
    >> print(json.dumps(sr.getdoc(), sort_keys=True, indent=4))
    """

    def __post_init__(self):
        super().__post_init__()
        self._items = {}
        self._doc = None

        # used when self.collect_results_by is set
        # this way we minimize our knowledge of the profile
        self._max_cluster_by_index = None
        self._observed_checks = {}

    @staticmethod
    def _set_metadata(identity, item):
        section, check, iterargs = identity
        # If section is None this is the main doc.
        # If check is None this is `section`
        # otherwise this `check`
        pass

    def omit_loglevel(self, msg) -> bool:
        """Determine if message is below log level."""
        return bool(self.loglevels) and (self.loglevels[0] > Status(msg))

    def _register(self, event):
        super()._register(event)
        key = event.identity.key

        # not item == True when item is empty
        item = self._items.get(key, {})
        if not item:
            self._items[key] = item
            # init
            if event.status in (START, END) and not item:
                item.update({"result": None, "sections": []})
                if self.collect_results_by:
                    # give the consumer a clue that/how the sections
                    # are structured differently.
                    item["clusteredBy"] = self.collect_results_by
            if event.status == SECTIONSUMMARY:
                item.update({"key": key, "result": None, "checks": []})
            if event.identity.check:
                check = event.identity.check
                item.update({"key": key, "result": None, "logs": []})
                if self.collect_results_by:
                    if self.collect_results_by == "*check":
                        if check.id not in self._observed_checks:
                            self._observed_checks[check.id] = len(self._observed_checks)
                        index = self._observed_checks[check.id]
                        value = check.id
                    else:
                        index = dict(event.identity.iterargs).get(
                            self.collect_results_by, None
                        )
                        value = None
                        if self.runner:
                            value = self.runner.get_iterarg(
                                self.collect_results_by, index
                            )

                    if index is not None:
                        if self._max_cluster_by_index is not None:
                            self._max_cluster_by_index = max(
                                index, self._max_cluster_by_index
                            )
                        else:
                            self._max_cluster_by_index = index

                    item["clustered"] = {
                        "name": self.collect_results_by,
                        # 'index' is None if this check did not require self.results_by
                        "index": index,
                    }
                    if (
                        value
                    ):  # Not set if self.runner was not defined on initialization
                        item["clustered"]["value"] = value

        if event.identity.check:
            check = event.identity.check
            item["description"] = check.description
            if check.documentation:
                item["documentation"] = check.documentation
            if check.rationale:
                item["rationale"] = check.rationale
            if check.experimental:
                item["experimental"] = check.experimental
            if check.severity:
                item["severity"] = check.severity
            if item["key"][2] != ():
                item["filename"] = self.runner.get_iterarg(*item["key"][2][0])

        if event.status == END:
            item["result"] = event.message  # is a Counter
        if event.status == SECTIONSUMMARY:
            _, item["result"] = event.message  # message[1] is a Counter
        if event.status == ENDCHECK:
            item["result"] = event.message.name  # is a Status
        if event.status >= DEBUG:
            item["logs"].append(
                {
                    "status": event.status.name,
                    "message": f"{event.message}",
                    "traceback": getattr(event.message, "traceback", None),
                }
            )

    def getdoc(self):
        if not self._ended:
            raise Exception("Can't create doc before END status was recevived.")
        if self._doc is not None:
            return self._doc
        doc = self._items[Identity(None, None, None).key]
        seen = set()
        # this puts all in the original order
        for identity in self._order:
            key = identity.key
            sectionKey = Identity(identity.section, None, None).key
            sectionDoc = self._items[sectionKey]

            check = self._items[key]
            if self.collect_results_by:
                if not sectionDoc["checks"]:
                    clusterlen = self._max_cluster_by_index + 1
                    if self.collect_results_by != "*check":
                        # + 1 for rests bucket
                        clusterlen += 1
                    sectionDoc["checks"] = [[] for _ in range(clusterlen)]
                index = check["clustered"]["index"]
                if index is None:
                    # last element collects unclustered
                    index = -1
                sectionDoc["checks"][index].append(
                    check
                )  # pytype: disable=attribute-error
            else:
                sectionDoc["checks"].append(check)
            if sectionKey not in seen:
                seen.add(sectionKey)
                doc["sections"].append(sectionDoc)
        self._doc = doc
        return doc

    def write(self):
        import json

        with open(self.output_file, "w", encoding="utf-8") as fh:
            json.dump(self.getdoc(), fh, sort_keys=True, indent=4)
        print(f'A report in JSON format has been saved to "{self.output_file}"')
