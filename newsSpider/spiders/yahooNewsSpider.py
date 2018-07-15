import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


class YahooNewsSpider(CrawlSpider):
    name = 'yahoo'

    # scrapy + splash

    allowed_domains = ['tw.news.yahoo.com']
    # start_urls = ['https://tw.news.yahoo.com']
    # start_urls = ["https://tw.news.yahoo.com/technology"]
    # start_urls = ['https://tw.news.yahoo.com/tech-development']
    start_urls = ['https://tw.news.yahoo.com/%E6%8B%8D%E6%89%8B%E6%A9%9F%E5%99%A8%E4%BA%BA-%E5%8F%AF%E4%BB%A5%E4%BE%9D%E7%85%A7%E4%B8%8D%E5%90%8C%E5%A0%B4%E5%90%88%E8%87%AA%E8%A8%82%E6%8B%8D%E6%89%8B%E7%AF%80%E5%A5%8F-021600616.html']
    # rules = [
    #     Rule(LinkExtractor(allow='\.html'), callback='parse_result', process_request="use_splash")
    # ]

    def __init__(self):

        # lua script
        self.script = """
            function main(splash, args)
                local num_scrolls = 5
                local scroll_delay = 1.0
                local scroll_to = splash:jsfunc("window.scrollTo")
                local get_body_height = splash:jsfunc("function() {return document.body.scrollHeight}")

                assert(splash:go(args.url))
                splash:wait(splash.args.wait)

                for _ = 1, num_scrolls do
                    scroll_to(0, get_body_height())
                    splash:wait(scroll_delay)
                end 
                
                return splash:html()

            end
        """
        # end of lua
        self.splash_args = {'lua_source': self.script, 'wait': 0.5}

    def start_requests(self):

        for url in self.start_urls:
            yield SplashRequest(url, callback=self.parse_news_content, args=self.splash_args, endpoint='execute')

    def parse_news_links(self, response):
        print(response)

        LINK_SELECTOR = 'h3 a[href$=html]::attr(href)'
        links = response.css(LINK_SELECTOR).extract()

        base_url = 'https://tw.news.yahoo.com'
        for link in links:
            news_url = base_url + link
            # yield scrapy.Request(news_url, callback=self.parse_news_content)
            yield SplashRequest(news_url, callback=self.parse_news_content, args=self.splash_args, endpoint='execute')
            break

    def parse_news_content(self, response):
        print('parse_news_content')
        # print(response.url)
        # print(response.text)
        title = response.xpath("//div[@class='canvas-header']/h1/text()").extract()
        content = response.xpath("//p[@class='canvas-text']/text()").extract()
        print(title)
        print(content)


# import requests
#
# url = "https://tw.news.yahoo.com"
# res = requests.get(url)
# print(res.text)
