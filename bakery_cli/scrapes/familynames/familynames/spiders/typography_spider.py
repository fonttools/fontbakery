from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class TypographySpider(Spider):

    name = 'typography'
    allowed_domains = ['typography.com']
    start_urls = [
        'http://www.typography.com/'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//ul[preceding-sibling::span/text()="Fonts"]/li/a/text()')
        result = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            result.append(ffi)
        return result

