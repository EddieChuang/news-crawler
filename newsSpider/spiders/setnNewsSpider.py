import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import NewsspiderItem


class SetnNewsSpider(CrawlSpider):
    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = []

    page = 6
    # groupId = ['4', '5', '7']  # ['生活', '國際', '科技']
    groupId = ['7']
    for gid in range(len(groupId)):
        for p in range(page):
            start_urls.append('https://www.setn.com/ViewAll.aspx?PageGroupID={0}&p={1}'.format(groupId[gid], p + 1))

    rules = [Rule(LinkExtractor(allow=['/News.aspx']), callback='parse_news')]

    def parse_news(self, response):

        cat = ''.join(response.xpath("//li[@class='active']/a/text()").extract())
        title = ''.join(response.xpath("//h1[@class='news-title-3']/text()").extract())
        content = '。'.join(response.xpath("//div[@id='Content1']/p/text()").extract())
        time = ''.join(response.xpath("//time[@class='page-date']/text()").extract()).split(' ')[0]
        newsItem = NewsspiderItem(name=self.name, cat=cat, title=title, content=content, time=time)
        return newsItem
