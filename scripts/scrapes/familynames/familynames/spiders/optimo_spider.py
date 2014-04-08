from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class OptimoSpider(Spider):

    name = 'optimo'
    allowed_domains = ['optimo.ch']
    start_urls = [
        'http://www.optimo.ch/typefaces.html'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//h3/a[@title]/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
