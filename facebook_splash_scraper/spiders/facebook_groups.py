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

    name = 'facebook_groups'

    # This will setup settings variable to get constant from settings.py such as SCROLLS (scrolling number)

    settings = get_project_settings()

    # Xpath variables to use to get elements when crawling

    xpath_post_link = "_52jc _5qc4 _78cz _24u0 _36xo"

    xpath_user_profile_1 = "_52jd _52jb _52jh _5qc3 _4vc- _3rc4 _4vc-"

    xpath_user_profile_2 = "_52jd _52jb _52jg _5qc3 _4vc- _3rc4 _4vc-"

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

        # Get Facebook Account from settings.py

        with open('./cookies/cookie_test.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)

        # Get groups list

        groups = self.settings.get("GROUPS")

        for url in groups:

            # Split string to get group ID

            group = str(url.split("/")[-1])

            # Use group ID to name groups html files for later storing and accessing to extract xpath

            with open( "./groups/html/group_html_" + group + '.html', 'w+') as out:
                out.write('')

            # Send splash request with cookies to get full html of each groups

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
                    "group": group
                }
            )

    def parse_links(self, response):

        # Store each return groups html to their corresponding html file named with their own group ID

        with open( "./groups/html/group_html_" + response.meta["group"] + '.html', 'w+') as out:
            out.write(response.text)

        # Extract xpath to get more information of each posts scraped from groups pages

        links = response.xpath("//div[@class='" + self.xpath_post_link + "']")

        # print("=====================", links)

        output_links = []

        for link_xpath in links:
            
            link = link_xpath.xpath("./a/@href").get()

            if link == "#":
                break
            
            if "permalink" not in str(link):
                link = "https://facebook.com" + link.split("&refid")[0]


            link = link.split("/?")[0]

            post = str(link.split("/")[-1])

            result = {
                "post": post,
                "link": link.replace("m.",""),
            }

            output_links.append(result)

        # Dump posts list with their additional information such as timestamp to groups json filles (named with group ID) for the third spider to access and get

        with open("./groups/json/group_posts_" + str(response.meta["group"]) + '.json', 'w+') as jsonfile:
            json.dump(output_links, jsonfile, ensure_ascii=False, indent = 4)
