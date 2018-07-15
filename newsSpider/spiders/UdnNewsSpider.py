from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import NewsspiderItem

class UdnNewsSpider(CrawlSpider):
    name = 'udn'
    domain = ['udn.com']
    start_urla = []


    