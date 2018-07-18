import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import NewsspiderItem
import re

class SetnNewsSpider(CrawlSpider):
    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = []

    page = 6
    groupId = ['2', '4', '5', '7', '34']  # 財經(2), 生活(4), 國際(5), 科技(7), 運動(34)
    # groupId = ['7']
    for gid in groupId:
        for p in range(page):
            start_urls.append('https://www.setn.com/ViewAll.aspx?PageGroupID={0}&p={1}'.format(gid, p + 1))

    rules = [Rule(LinkExtractor(allow=['/News.aspx']), callback='parse_news')]

    def parse_news(self, response):

        cat = ''.join(response.xpath("//li[@class='active']/a/text()").extract())
        title = ''.join(response.xpath("//h1[@class='news-title-3']/text()").extract())
        content = self.clear_content(response.xpath("//div[@id='Content1']/p//text()").extract()[1:])
        time = ''.join(response.xpath("//time[@class='page-date']/text()").extract()).split(' ')[0]

        if self.time_filter(time, '2018/01/1', '2018/07/17') and not content == "":
            newsItem = NewsspiderItem(name=self.name, cat=cat, title=title, content=content, time=time)
            return newsItem

    def clear_content(self, article):

        content = ''
        ignore_patterns = ['.*▲.*', '.*◆.*', '.*★.*']
        replace_patterns = ['\（.*\）', '\(.*\)', '.*window.location.*']
        replace_char = [' ', '　', '\n']
        ignore_next_char = []
        ignore, ignore_next = False, False
        for paragraph in article:
            print("############################################")
            print("before: {}".format(paragraph))

            if ignore_next:
                ignore_next = False
                continue
            for char in ignore_next_char:
                if char in paragraph:
                    ignore = True
                    ignore_next = True
                    break

            for pattern in ignore_patterns:
                if re.match(pattern, paragraph):
                    ignore = True
                    break
            if ignore:
                ignore = False
                continue

            for char in replace_char:
                paragraph = paragraph.replace(char, '')
            for pattern in replace_patterns:
                paragraph = re.sub(pattern, '', paragraph)
            if not paragraph == "":
                content += paragraph
            print("after: {}".format(paragraph))
            print("############################################")

        return content

    def time_filter(self, time, start, end):
        return end >= time >= start
