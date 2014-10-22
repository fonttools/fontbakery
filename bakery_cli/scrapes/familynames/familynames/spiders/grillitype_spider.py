from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class SwissTypefacesSpider(Spider):

    name = 'grillitype'
    allowed_domains = ['grillitype.com']
    start_urls = [
        'http://www.grillitype.com/typefaces'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//div[re:test(@class, "view-content")]/ul/li/a/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
