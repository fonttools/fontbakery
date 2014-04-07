from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class EuropaTypeSpider(Spider):

    name = 'europatype'
    allowed_domains = ['europatype.com']
    start_urls = [
        'http://www.europatype.com/'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//nav[@id="mainnav"]/ul/li/a/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
