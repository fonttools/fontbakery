from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class SwissTypefacesSpider(Spider):

    name = 'swisstypefaces'
    allowed_domains = ['swisstypefaces.com']
    start_urls = [
        'http://www.swisstypefaces.com/fonts/'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//h2[re:test(@class, "collection_text")]/a/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
