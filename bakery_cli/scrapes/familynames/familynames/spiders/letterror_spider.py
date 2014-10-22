from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from familynames.items import FontFamilyItem


class LetterrorSpider(CrawlSpider):

    name = 'letterror'
    allowed_domains = ['letterror.com']
    start_urls = [
        'http://letterror.com/fontcatalog/'
    ]

    rules = (
        Rule(SgmlLinkExtractor(allow=('/fontcatalog/.+', )), callback='parse_item'),
    )

    def parse_item(self, response):
        sel = Selector(response)
        items = sel.xpath('//h1[@id="teaser-headline"]/text()')
        r = []
        for item in items.extract():
            ffi = FontFamilyItem()
            ffi['title'] = item
            r.append(ffi)
        return r
