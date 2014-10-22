from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class TypeDifferentSpider(Spider):

    name = 'typedifferent'
    allowed_domains = [
        'typedifferent.com'
    ]
    start_urls = [
        'http://www.typedifferent.com/year-2013/'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//select[@id="name"]/option/text()')
        r = []
        for item in items.extract():
            if item == 'fontname':
                continue
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
