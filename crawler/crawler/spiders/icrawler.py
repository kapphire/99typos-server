# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class IcrawlerSpider(CrawlSpider):
    name = 'icrawler'
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.CrawlerPipeline': 300,
        }
    }
    print('==== icrawler spider started ====')

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]
        self.deny_urls = (r'/feed/.*', r'/login/.*')
        self.rules = [
            Rule(
                LinkExtractor(
                    canonicalize=True,
                    unique=True,
                    deny=self.deny_urls
                ),
                callback='parse_item',
                follow=True
            ),
        ]
        super(IcrawlerSpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        i = dict()
        i['links'] = list()
        i['imgs'] = list()

        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        for link in links:
            is_allowed = True
            for deny_url in self.deny_urls:
                deny_regexp = re.compile(deny_url)
                if deny_regexp.search(link.url):
                    is_allowed = False
            if is_allowed:
                i['links'].append(link.url)
        for image in response.xpath('//img/@src').extract():
            i['imgs'].append(response.urljoin(image))

        i['url'] = response.url
        i['body'] = response.body
        i['status'] = response.status
        return i
