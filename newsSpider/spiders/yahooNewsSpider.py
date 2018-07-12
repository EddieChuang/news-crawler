import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


class YahooNewsSpider(CrawlSpider):
    name = 'yahoo'

    # scrapy + splash

    allowed_domains = ['tw.news.yahoo.com']
    start_urls = ['https://tw.news.yahoo.com']
    # start_urls = ["https://tw.news.yahoo.com/technology"]
    # start_urls = ['https://tw.news.yahoo.com/tech-development']

    # rules = [
    #     Rule(LinkExtractor(allow='\.html'), callback='parse_result', process_request="use_splash")
    # ]

    def start_requests(self):
        # lua script
        script = """
            function main(splash, args)
                local num_scrolls = 10
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
        # for url in self.start_urls:
        #     yield SplashRequest(url, dont_process_response=True, args=splash_args, endpoint='execute', meta={'real_url': url})

        rules = [Rule(LinkExtractor(allow='[.]*'), callback='parse_result', process_request="splash_request")]

    def splash_request(self, request):
        # lua script
        script = """
            function main(splash, args)
                local num_scrolls = 10
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
        return SplashRequest(url=request.url, dont_process_response=True, endpoint='execute', args=splash_args,
                             meta={'real_url': request.url})

    def _requests_to_follow(self, response):

        seen = set()
        new_response = response.replace(url=response.meta.get('real_url'))
        for n, rule in enumerate(self.rules):
            links = [link for link in rule.link_extractor.extract_links(new_response) if link not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
                for link in links:
                    seen.add(link)
                    r = self._build_request(n, link)
                    yield rule.process_links(r)


    def parse_result(self, response):
        print(response.url)

        # LINK_SELECTOR = 'h3 a::attr(href)'
        # links = response.css(LINK_SELECTOR).extract()
        #
        # for link in links:
        #     print(link)

# import requests
#
# url = "https://tw.news.yahoo.com"
# res = requests.get(url)
# print(res.text)
