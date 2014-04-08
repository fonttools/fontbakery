from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class CommercialTypeSpider(Spider):

    name = 'commercialtype'
    allowed_domains = [
        'commercialtype.com'
    ]
    start_urls = [
        'https://commercialtype.com/typefaces'
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//div[@class="superfamily_families"]')
        r = []
        for item in items:
            families_list = item.xpath('./div[re:test(@class, "families_list")]/a/text()').extract()
            if families_list:
                for familyname in families_list:
                    ffi = FontFamilyItem()
                    ffi['title'] = familyname
                    r.append(ffi)
            else:
                for it in item.xpath('./a/text()').extract():
                    ffi = FontFamilyItem()
                    ffi['title'] = it
                    r.append(ffi)
        return r
