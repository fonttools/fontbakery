#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.command import ScrapyCommand
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings


class AllSpidersCommand(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        settings = get_project_settings()

        for spider_name in self.crawler.spiders.list():
            crawler = Crawler(settings)
            crawler.configure()
            spider = crawler.spiders.create(spider_name)
            crawler.crawl(spider)
            crawler.start()

        self.crawler.start()
