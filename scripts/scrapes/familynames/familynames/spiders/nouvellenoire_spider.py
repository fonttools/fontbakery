from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class NouvelleNoireSpider(Spider):

    name = 'nouvellenoire'
    allowed_domains = [
        'nouvellenoire.ch'
    ]
    start_urls = [
        'https://nouvellenoire.ch/collections/all'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//div[@class="details"]/a/h4/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            try:
                ffi['title'] = item.split('|')[1].strip()
            except IndexError:
                ffi['title'] = item
            r.append(ffi)
        return r
