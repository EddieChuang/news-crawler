import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from ..items import NewsspiderItem
import json


class UdnNewsSpider(CrawlSpider):
    name = 'udn'
    domain = ['udn.com']
    start_urls = []

    groupId = ['13']  # 科技
    for gid in groupId:
        start_urls.append('https://udn.com/news/breaknews/1/{0}#breaknews'.format(gid))

    # rules = [Rule(LinkExtractor(allow=['']), callback='parse_news')]

    def __init__(self):

        # lua script
        # 滾動頁面取得未顯示的內容，並點擊"看更多內容"載入舊新聞
        self.script = """
            function main(splash, args)
                local num_scrolls = 10
                local scroll_delay = 1.0
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
        content = ''.join(response.xpath("//div[@id='story_body_content']/p//text()").extract()).replace('。。', '。')
        time = ''.join(response.xpath("//div[@class='story_bady_info_author']/span/text()").extract()).split(' ')[0].replace('-', '/')   # yyyy/mm/dd

        # print(cat)
        # print(title)
        # print(content)
        # print(time)
        newsItem = NewsspiderItem(name=self.name, cat=cat, title=title, content=content, time=time)
        return newsItem
