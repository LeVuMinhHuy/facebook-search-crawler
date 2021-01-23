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

    # Convert datetime get from facebook html to timestamp

    def _convert_to_timestamp(self, the_input):

        ts = -1

        for each in  ["Hôm qua"]:
            if each in the_input:
                today = datetime.now()

                the_time = the_input.split(" ")[-1].split(":")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=int(the_time[0]), minute=int(the_time[1])) - timedelta(days=1)

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["tháng"]:
            if each in the_input:
                if "," in the_input:

                    the_time = the_input.split(" ")

                    the_hrs_mins = the_time[-1].split(":")

                    d = datetime(year=int(the_time[3]), month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                    ts = int(time.mktime(d.utctimetuple()))

                    return ts

                else:

                    today = datetime.now()

                    the_time = the_input.split(" ")

                    the_hrs_mins = the_time[-1].split(":")

                    d = datetime(year=today.year, month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                    ts = int(time.mktime(d.utctimetuple()))

                    return ts
        
        for each in  ["giờ"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(hours=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["phút"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(minutes=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["giây"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(seconds=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))
        
                return ts

    

    def start_requests(self):

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

            times = link_xpath.xpath("./a//text()").get()

            times = self._convert_to_timestamp(times)

            link = link.split("/?")[0]

            post = str(link.split("/")[-1])

            result = {
                "post": post,
                "link": link.replace("m.",""),
                "timestamp": times
            }

            output_links.append(result)

        # Dump posts list with their additional information such as timestamp to groups json filles (named with group ID) for the third spider to access and get

        with open("./groups/json/group_posts_" + str(response.meta["group"]) + '.json', 'w+') as jsonfile:
            json.dump(output_links, jsonfile, ensure_ascii=False)
