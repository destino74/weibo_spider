# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy import Request

from weibo_spider.items import WeiboSpiderItem


class WeiboSpider(CrawlSpider):
    name = 'weibo'
    allowed_domains = ['www.weibo.com']
    start_urls = ['http://weibo.com/login.php']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={}, headers={})  # 这里填入保存的cookies


    def parse_item(self, response):
        i = WeiboSpiderItem()
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
