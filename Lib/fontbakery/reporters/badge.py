"""
Serialization reporter which specifically formats its JSON in a style suitable
for use by a shields.io dynamic endpoint (https://shields.io/endpoint)

Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
import os
import re

from fontbakery.reporters.serialize import SerializeReporter

minibadge = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 294 294"><style>.a{fill:#333;}</style><path d="M147 0C228 0 294 66 294 147 294 228 228 294 147 294 66 294 0 228 0 147 0 66 66 0 147 0Z" fill="#b3eeff"/><path d="M102 90C30 56 28 161 92 148L98 236C132 234 162 233 184 235L189 162C189 153 177 166 142 146 169 151 185 150 195 145 227 155 253 141 246 111 240 88 217 81 185 76 138 70 138 113 102 90Z" fill="#fff"/><path d="M105 162L91 162 93 238 146 237 146 224 106 225 106 207 142 206 141 194 106 195Z" class="a"/><path d="M196 162L195 195 159 194 158 206 194 207 193 226 154 224 154 236 206 239 209 163Z" class="a"/><path d="M204 72L203 84 205 85C212 86 218 88 223 90 227 92 230 95 233 98 236 101 238 104 239 107 240 110 240 114 240 117 240 120 239 124 237 127 236 130 234 133 231 135 228 137 225 138 222 139 218 140 214 140 210 140 206 139 202 138 197 136 192 133 187 130 183 125L182 124 173 131 174 133C180 139 186 144 194 148 200 151 206 153 211 154 217 154 222 154 227 152 232 151 236 148 240 145 244 142 247 138 249 133 252 128 253 123 254 118 254 113 254 108 252 103 250 99 247 94 243 90 239 86 234 82 228 79 221 75 214 73 206 72Z" class="a"/><path d="M78 77C76 77 74 78 72 78 68 79 63 80 60 82 56 84 53 86 50 89 47 92 45 95 43 99 42 102 41 106 40 110 39 114 39 117 40 121 40 125 41 129 43 132 44 136 47 139 50 142 52 145 56 148 61 150 65 152 70 154 76 155 90 157 101 155 109 148L114 117 77 111 76 123 99 127 97 141C92 143 87 144 80 143 74 142 69 140 65 137 60 134 57 130 55 126 53 121 53 116 53 111 54 107 55 104 57 101 60 98 62 96 65 94 68 92 72 91 75 91 79 90 83 90 86 90 90 91 94 92 98 94 101 95 104 97 106 99L108 100 115 90 114 89C106 83 98 80 88 78 84 78 81 77 78 77Z" class="a"/><path d="M175 69C173 69 171 69 170 70 168 70 166 71 164 71 163 72 161 73 159 74L116 96 123 108 166 86C166 85 167 85 168 85 168 84 169 84 170 84 172 83 173 83 174 83 175 83 176 83 177 84 178 84 180 84 181 85 182 86 183 87 185 89 186 90 187 92 188 94 189 96 190 98 191 101L191 103 203 99 202 97C201 94 200 90 198 87 197 84 195 81 193 78 191 76 189 74 187 73 185 72 183 71 181 70 179 69 177 69 175 69Z" class="a"/></svg>"""  # noqa:E501 pylint:disable=C0301


def color_for(fraction):
    if fraction > 0.9:
        return "brightgreen"
    elif fraction > 0.7:
        return "green"
    elif fraction > 0.5:
        return "yellow"
    elif fraction > 0.3:
        return "orange"
    return "red"


class BadgeReporter(SerializeReporter):
    def getdoc(self):
        doc = super().getdoc()
        sections = {}
        total_score = 0
        total_total = 0
        for section in doc["sections"]:
            key = section["key"][0]
            m = re.match("<Section: (.*)>", key)
            if m:
                key = m[1]
            score = 0
            out_of = 0
            error_state = False
            for check in section["checks"]:
                severity = check.get("severity", 5)
                if check["result"] == "SKIP":
                    continue
                if check["result"] == "ERROR":
                    error_state = True
                    break
                out_of += severity
                if check["result"] == "PASS":
                    score += severity
            total_score += score
            total_total += out_of
            sections[key] = self.make_section(key, error_state, score, out_of)
        sections["overall"] = self.make_section(
            "FontBakery QA", False, total_score, total_total
        )
        self._doc = sections
        return sections

    @staticmethod
    def make_section(key, error_state, score, out_of):
        if error_state:
            message = "ERRORED"
            color = "red"
        elif out_of:
            message = "%i%%" % (score / out_of * 100)
            color = color_for(score / out_of)
        else:
            message = "SKIP"
            color = "inactive"
        return {
            "schemaVersion": 1,
            "label": key,
            "message": message,
            "color": color,
            "logoSvg": minibadge,
        }

    def write(self):
        if not os.path.exists(self.output_file):
            os.mkdir(self.output_file)

        import json

        doc = self.getdoc()
        for section, data in doc.items():
            if section.startswith("fontbakery."):  # Not a "real" name
                continue

            sanitize_name = section.replace(" ", "")
            filename = os.path.join(self.output_file, sanitize_name) + ".json"
            with open(filename, "w", encoding="utf-8") as fh:
                json.dump(data, fh, sort_keys=True, indent=4)

        print(f'A set of badges in JSON format has been saved to "{self.output_file}/"')
