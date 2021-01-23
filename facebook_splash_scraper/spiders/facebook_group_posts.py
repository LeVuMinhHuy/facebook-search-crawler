# ===================================================
#  Title:  Get posts html for later xpath extraction
#  Author: Huỳnh Ngọc Thiện
#  Date:   Jan 9 2021
# ===================================================

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
import time 

class FacebookSpider(scrapy.Spider):

    # This name will be use to call the crawling spider, for example: scrapy crawl facebook_posts

    name = 'facebook_group_posts'

    # This will setup settings variable to get constant from settings.py such as SCROLLS (scrolling number)

    settings = get_project_settings()

    # Xpath variables to use to get elements when crawling

    xpath_view_more_cmt = "j83agx80 fv0vnmcu hpfvmrgz"

    xpath_view_more_info = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p"

    # Lua script to interact with js in the website while crawling

    script_links = """

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

            scroll_to(0, get_body_height())
            assert(splash:wait(1))

            local more = true

            while(more)
            do

                more = false

                local spans = splash:select_all("span[class='""" + xpath_view_more_cmt + """']")

                for _, _span in ipairs(spans) do
                    assert(_span:mouse_click())
                    more = true
                end

                assert(splash:wait(5))

                splash:set_viewport_full()

                local scroll_to = splash:jsfunc("window.scrollTo")
                local get_body_height = splash:jsfunc(
                    "function() {return document.body.scrollHeight;}"
                )

                scroll_to(0, get_body_height())
                assert(splash:wait(1))

                local divs = splash:select_all("div[class='""" + xpath_view_more_info + """']")

                for _, _ in ipairs(divs) do
                    local _div = splash:select("div[class='""" + xpath_view_more_info + """']")
                    if _div ~= nil then
                        assert(_div:mouse_click())
                    end
                end

                assert(splash:wait(5))

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

        # Get groups list to access posts that are in same groups and stored in same groups json files

        groups = self.settings.get("GROUPS")

        for url in groups:

            # Split string to get group ID

            group = str(url.split("/")[-1])

            # Use group ID to access groups json files that contain posts list in the same group for later storing and accessing to extract xpath

            with open("./groups/json/group_posts_" + group + '.json', 'r') as jsonfile:
                posts = json.load(jsonfile)
            
            for post in posts:

                # Use post ID from posts list inside each groups json files to access posts html files

                with open( "./posts/html/post_html_" + post["post"] + '.html', 'w+') as out:
                    out.write('')

                # Send splash request with cookies to get full html of each posts

                yield SplashRequest(
                    url=post["link"],
                    callback=self.parse,
                    session_id="test",
                    meta={
                        "splash": {
                            "endpoint": "execute", 
                            "args": {
                                "lua_source": self.script_links,
                                "cookies": cookies,
                                "timeout": 3600
                            }
                        },
                        "post": post["post"]
                    }
                )

                # time.sleep(30)
    
    def parse(self, response):

        # Store each return posts html to their corresponding html file named with their own post ID

        with open( "./posts/html/post_html_" + response.meta["post"] + '.html', 'w+') as out:
            out.write(response.text)
