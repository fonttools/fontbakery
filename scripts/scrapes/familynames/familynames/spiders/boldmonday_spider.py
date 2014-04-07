from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import FontFamilyItem


class BoldMondaySpider(Spider):

    name = 'boldmonday'
    allowed_domains = ['boldmonday.com']
    start_urls = [
        'http://www.boldmonday.com/en/retail_fonts/'
    ]

    def parse_font_page(self, response):
        sel = Selector(response)
        item = sel.xpath('//h1/text()').extract()[0]
        ffi = FontFamilyItem()
        ffi['title'] = item
        return ffi

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//div[@id="content_fontcatalog"]/ul/li/a/@href')
        for url in items.extract():
            yield Request('http://www.boldmonday.com/' + url.lstrip('../'), callback=self.parse_font_page)
