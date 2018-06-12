# -*- coding: utf-8 -*-
import scrapy


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    #allowed_domains = ['www.douban.com']
    start_urls = ['https://www.douban.com/group/481977/discussion?start=50']
    #start_urls = ['http://www.zgyz001.com/']

    def parse(self, response):
        print "this is the first douban spide"
        filename = 'douban-%s.html' % '50'
        with open(filename, 'wb') as f:
            f.write(response.body)
        pass
