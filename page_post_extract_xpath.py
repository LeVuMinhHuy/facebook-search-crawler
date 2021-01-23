# =========================================================================
#  Title:  Extract neede features through xpath from posts html files that
#  Author: Huỳnh Ngọc Thiện
#  Date:   Jan 9 2021
# =========================================================================

import lxml.html
from scrapy.utils.project import get_project_settings
import json
import os
import time
from datetime import datetime, timedelta

settings = get_project_settings()

pages = settings.get("PAGES")

for url in pages:

    page = str(url.split("/")[-1])

    with open("./pages/json/page_posts_" + page + '.json', 'r') as jsonfile:
        posts = json.load(jsonfile)
        
    for post in posts:

        if os.path.isfile("./posts/html/post_html_" + post["post"] + '.html'):
            htmls = ""
            with open("./posts/html/post_html_" + post["post"] + '.html', 'r') as f:
                htmls = f.read()

            htmls = lxml.html.fromstring(str(htmls))

            post_message = htmls.xpath("//div[@class='_5rgt _5nk5']//text()")

            post["post_message"] = post_message

            post_comment =htmls.xpath("//div[@class='_2b06']/div[2]//text()")

            post["post_comment"] = post_comment

            with open( "./posts/json/page/post_" + post["post"] + '.json', 'w+') as jsonfile:
                json.dump(post, jsonfile, ensure_ascii=False, indent=4)
        
