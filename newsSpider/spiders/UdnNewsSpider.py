import json
import re
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest

from ..items import NewsspiderItem


class UdnNewsSpider(CrawlSpider):
    name = 'udn'
    domain = ['udn.com']
    start_urls = []

    # groupId = ['13']
    groupId = ['4', '5', '6', '7', '9', '11', '12', '13']  # 兩岸(4), 國際(5), 財經(6), 運動(7), 生活(9), 股市(11), 文教(12), 數位(13)
    for gid in groupId:
        start_urls.append('https://udn.com/news/breaknews/1/{0}#breaknews'.format(gid))

    # rules = [Rule(LinkExtractor(allow=['']), callback='parse_news')]

    def __init__(self):

        # lua script
        # 滾動頁面取得未顯示的內容，並點擊"看更多內容"載入舊新聞
        self.script = """
            function main(splash, args)
                local num_scrolls = 150
                local scroll_delay = 0
                local scroll_to = splash:jsfunc("window.scrollTo")
                local click_more = splash:jsfunc("function() { return document.getElementsByClassName('bbox')[0].click() }")
                local get_body_height = splash:jsfunc("function() { return document.body.scrollHeight }")

                assert(splash:go(args.url))
                splash:wait(splash.args.wait)

                for _ = 1, num_scrolls do
                    scroll_to(0, get_body_height())
                    click_more()
                    splash:wait(scroll_delay)
                end 
                
                local get_links = splash:jsfunc([[function() { 
                    var target = document.querySelectorAll('dt > a[target]')
                    var links = Array.apply(null, target).map(ele => ele.href).filter(href => href.includes('/news/story/'))
                    return links
                }]])
                
                return {links=get_links()}
                
            end
        """
        # end of lua
        self.splash_args = {'lua_source': self.script, 'wait': 0.5}

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.parse_news_links, args=self.splash_args, endpoint='execute')

    def parse_news_links(self, response):

        res = json.loads(response.text)
        links = res['links']
        print(len(links))
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_news_content)

    def parse_news_content(self, response):
        # print(response.url)
        cat = ''.join(response.xpath("//div[@id='scroller']/dl/dt[@class='active']/a/text()").extract())
        title = ''.join(response.xpath("//h1[@id='story_art_title']/text()").extract())

        # print("#######################################################")
        # print(response.css("#story_body_content p *::text").extract())
        # print("#######################################################")
        content = self.clear_content(response.xpath("//div[@id='story_body_content']/p//text()").extract())

        time = ''.join(response.xpath("//div[@class='story_bady_info_author']/span/text()").extract()).split(' ')[
            0].replace('-', '/')  # yyyy/mm/dd
        # print(cat)
        # print(title)
        # print(content)
        # print(time)
        # time format: yyyy/mm/dd
        if self.time_filter(time, '2018/01/1', '2018/07/17'):
            newsItem = NewsspiderItem(name=self.name, cat=cat, title=title, content=content, time=time)
            return newsItem

    def clear_content(self, article):

        content = ''
        ignore_patterns = ['.*圖／.*', '.*記者.*／攝影.*']
        replace_patterns = ['\（.*\）', '\(.*\)', '.*window.location.*']
        replace_char = [' ', '　', '\n', 'facebook', '分享']
        ignore_next_char = ['圖擷自']
        ignore, ignore_next = False, False
        for paragraph in article:
            print(paragraph)

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

        return content

    def time_filter(self, time, start, end):
        return end >= time >= start
