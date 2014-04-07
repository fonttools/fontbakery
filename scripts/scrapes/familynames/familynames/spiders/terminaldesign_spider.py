from scrapy.selector import Selector
from scrapy.spider import Spider

from familynames.items import TerminalDesignItem


class TerminalDesignSpider(Spider):
    name = "terminaldesign"
    allowed_domains = ["terminaldesign.com"]
    start_urls = [
        "http://www.terminaldesign.com/fonts/"
    ]

    def parse(self, response):
        sel = Selector(response)
        fonts = sel.xpath('//div["data-promo-name"]/@data-promo-name').extract()
        items = []
        for fontname in fonts:
            tdi = TerminalDesignItem()
            tdi['title'] = fontname
            items.append(tdi)
        return items
