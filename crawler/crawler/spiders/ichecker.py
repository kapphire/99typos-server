# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class IcheckerSpider(CrawlSpider):
    name = 'ichecker'
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.CheckerPipeline': 300,
        }
    }
    print('==== ichecker spider started ====')

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]
        self.rules = (
           Rule(LinkExtractor(unique=True), callback='parse_item', follow=True),
        )
        super(IcheckerSpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        i = {}
        i['url'] = response.url
        i['body'] = response.body
        i['status'] = response.status
        return i
