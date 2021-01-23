# ===========================================================
#  Title:  Get posts links and group html for later crawling
#  Author: Huỳnh Ngọc Thiện
#  Date:   Jan 9 2021
# ===========================================================

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
import time
from datetime import datetime, timedelta


class FacebookSpider(scrapy.Spider):
    # This name will be use to call the crawling spider, for example: scrapy crawl facebook_links

    name = 'facebook_pages'

    # This will setup settings variable to get constant from settings.py such as SCROLLS (scrolling number)

    settings = get_project_settings()

    # Xpath variables to use to get elements when crawling

    xpath_post_link = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"

    # Lua script to interact with js in the website while crawling

    script = """

        function main(splash, args)

            splash:init_cookies(splash.args.cookies)

            assert(splash:go{
                splash.args.url,
                headers=splash.args.headers
            })

            assert(splash:wait(5))

            splash:set_viewport_full()

            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )

            for _ = 1, """ + str(settings.get("SCROLLS")) + """ do
                scroll_to(0, get_body_height())                
                assert(splash:wait(1))
            end 

            assert(splash:wait(5))

            local spans = splash:select_all("a[class='""" + xpath_post_link + """']")

            for _, _span in ipairs(spans) do
                assert(_span:mouse_hover{})
            end

            local entries = splash:history()
            local last_response = entries[#entries].response

            return {
                cookies = splash:get_cookies(),
                headers = last_response.headers,
                html = splash:html()
            }
        end

    """

    def start_requests(self):

        with open('./cookies/cookie_test.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)

        pages = self.settings.get("PAGES")

        for url in pages:
            print("==============", url)
            page = str(url.split("/")[-1])

            with open("./pages/html/page_html_" + page + '.html', 'w+') as out:
                out.write('')

            yield SplashRequest(
                url=url,
                callback=self.parse_links,
                session_id="test",
                meta={
                    "splash": {
                        "endpoint": "execute",
                        "args": {
                            "lua_source": self.script,
                            "cookies": cookies,
                            "headers": {
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
                            }
                        }
                    },
                    "page": page
                }
            )

    def parse_links(self, response):

        with open("./pages/html/page_html_" + response.meta["page"] + '.html', 'w+') as out:
            out.write(response.text)

        links = response.xpath("//a[@class='" + self.xpath_post_link + "']")

        output_links = []

        for link_xpath in links:

            link = link_xpath.xpath("./@href").get()

            if link == "#":
                break

            link = link.split("/?")[0]

            post = str(link.split("/")[-1])

            result = {
                "post": post,
                "link": link.replace("m.", ""),
            }

            output_links.append(result)

        with open("./pages/json/page_posts_" + str(response.meta["page"]) + '.json', 'w+') as jsonfile:
            json.dump(output_links, jsonfile, ensure_ascii=False)

