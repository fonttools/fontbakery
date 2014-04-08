import htmlentitydefs
import re

from scrapy.spider import Spider

from familynames.items import FontFamilyItem


def convert(s):
    """ Take an input string s, find all things that look like SGML character
        entities, and replace them with the Unicode equivalent.
    """
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass
    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if name in htmlentitydefs.name2codepoint:
            s = s.replace(hit,
                          unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s


class TeffSpider(Spider):

    name = 'teff'
    allowed_domains = ['teff.nl']
    start_urls = [
        'http://www.teff.nl/js/global.js'
    ]

    def parse(self, response):
        text = response.body_as_unicode().strip().encode('utf8')
        items = re.findall(r"myFonts\[\d*\]=\['.*?', '(.*?)', '\d*'\]", text)
        r = []
        for item in items:
            ffi = FontFamilyItem()
            ffi['title'] = convert(item)
            r.append(ffi)
        return r
