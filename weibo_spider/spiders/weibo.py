# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from weibo_spider.items import WeiboSpiderItem
from weibo_spider.spiders.login_api import get_login_cookie


class WeiboSpider(CrawlSpider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    start_urls = ['http://www.weibo.com/u/1674242970']  # 不加www,则匹配不到cookie, get_login_cookie()方法正则代完善
    rules = (
        Rule(LinkExtractor(allow=r'^http:\/\/(www\.)?weibo.com/[a-z]/.*'),  # 微博个人页面的规则,或/u/或/n/后面跟一串数字
             process_request='process_request',
             callback='parse_item', follow=True), )
    cookies = None

    def process_request(self, request):
        request = request.replace(**{'cookies': self.cookies})
        return request

    def start_requests(self):
        for url in self.start_urls:
            if not self.cookies:
                self.cookies = get_login_cookie(url)    # 得到该url下的cookie
            yield Request(url, dont_filter=True, cookies=self.cookies, meta={'cookiejar': 1})  # 这里填入保存的cookies

    def extract_weibo_response(self, response):     # 提取weibo内容,替换response
        script_set = response.xpath('//script')
        script = ''
        for s in script_set:
            try:
                s_text = s.xpath('text()').extract()[0].encode('utf8').replace(r'\"', r'"').replace(r'\/', r'/')
            except:
                return response
            if s_text.find('WB_feed_detail') > 0:
                script = s_text
                break
        kw = {'body': script}
        response = response.replace(**kw)
        return response

    def _parse_response(self, response, callback, cb_kwargs, follow=True):  # 继承crawlspider这个方法,这个方法在解析页面/提取链接前调用
        response = self.extract_weibo_response(response)
        return super(WeiboSpider, self)._parse_response(response, callback, cb_kwargs, follow)

    def parse_item(self, response):
        msg_nodes = response.xpath('//*[@class="WB_feed WB_feed_profile"][2]/div')
        items = []
        if msg_nodes:
            for msg in msg_nodes:
                item = WeiboSpiderItem()
                try:
                    c = msg.xpath('.//div[@class="WB_detail"]/div/text()').extract()[0]
                    content = c[38:].encode('utf8')
                except Exception, e:
                    pass
                else:
                    item['content'] = content
                    item['url'] = response.url
                    items.append(item)
        return items











