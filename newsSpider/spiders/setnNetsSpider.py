import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class SetnNewsSpider(CrawlSpider):
    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = []
    rules = [Rule(LinkExtractor(allow=['/News.aspx']), callback='parse_news')]
    page = 6
    for i in range(page):
        start_urls.append('https://www.setn.com/ViewAll.aspx?PageGroupID=7&p={0}'.format(i+1))

    def parse_news(self, response):

        print(response.url)
