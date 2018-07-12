import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import NewsspiderItem

class SetnNewsSpider(CrawlSpider):

    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = []
    rules = [Rule(LinkExtractor(allow=['/News.aspx']), callback='parse_news')]
    page = 6
    for i in range(page):
        start_urls.append('https://www.setn.com/ViewAll.aspx?PageGroupID=7&p={0}'.format(i+1))

    def parse_news(self, response):

        title = ''.join(response.xpath("//h1[@class='news-title-3']/text()").extract())
        content = ''.join(response.xpath("//div[@id='Content1']/p/text()").extract())
        print(title)
        newsItem = NewsspiderItem(name=self.name, title=title, content=content)
        # return newsItem
