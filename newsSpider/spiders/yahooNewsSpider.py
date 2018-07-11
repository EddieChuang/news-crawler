import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


class YahooNewsSpider(CrawlSpider):
    name = 'yahoo'

    # allowed_domains = ['news.cnyes.com']
    # start_urls = ['https://news.cnyes.com/news/cat/headline']
    # rules = [Rule(LinkExtractor(allow=['/news/id/'], deny=['\/print']), 'parse_news', follow=True)]
    # def start_requests(self):
    #     urls = ['https://tw.money.yahoo.com/']
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)
    #
    # def parse(self, response):
    #     print(response.url)
    #     # print(response.body)
    #
    #     with open('money.html', 'wb') as file:
    #         file.write(response.body)




    # scrapy + splash

    allowed_domains = ['tw.news.yahoo.com']
    start_urls = ['https://tw.news.yahoo.com']
    # start_urls = ["https://tw.news.yahoo.com/technology"]

    def start_requests(self):
        # lua
        script = """
            function main(splash, args)
                local num_scrolls = 1
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

        splash_args = {'lua_source': script, 'wait': 2}
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_result, endpoint='execute', args=splash_args)

    def parse_result(self, response):
        print(response)

        LINK_SELECTOR = 'a'
        # LINK_SELECTOR = 'h3.MB\(5px\) a ::attr(href)'
        links = response.css(LINK_SELECTOR)

        for link in links:
            print(link)





# import requests
#
# url = "https://tw.news.yahoo.com"
# res = requests.get(url)
# print(res.text)
