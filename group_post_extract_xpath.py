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

# This will setup settings variable to get constant from settings.py such as SCROLLS (scrolling number)

settings = get_project_settings()

# Get groups list

groups = settings.get("GROUPS")

for url in groups:

    group = str(url.split("/")[-1])

    with open("./groups/json/group_posts_" + group + '.json', 'r') as jsonfile:
        posts = json.load(jsonfile)
        
    for post in posts:

        # Check if post was crawled and stored into html file or not

        if os.path.isfile("./posts/html/post_html_" + post["post"] + '.html'):
            htmls = ""
            with open("./posts/html/post_html_" + post["post"] + '.html', 'r') as f:
                htmls = f.read()

            # Parse string html in file into xpath objects

            htmls = lxml.html.fromstring(str(htmls))

            post_message = htmls.xpath("//div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']//text()")
            if(post_message == []):
                post_message = htmls.xpath("//div[@class='ecm0bbzt hv4rvrfc e5nlhep0 dati1w0a']//text()")

            post["post_message"] = post_message
            post["post_comment"] = []

            comments = htmls.xpath("//div[@class='cwj9ozl2 tvmbv18p']/ul/li")

            user_id_list = {}

            for comment in comments:

                post["post_comment"].append(comment.xpath(".//div[@class='l9j0dhe7 ecm0bbzt rz4wbd8a qt6c0cv9 dati1w0a j83agx80 btwxx1t3 lzcic4wl']//div[@class='ecm0bbzt e5nlhep0 a8c37x1j']//text()"))

                replies = comment.xpath(".//div[@class='kvgmc6g5 jb3vyjys rz4wbd8a qt6c0cv9 d0szoon8']")

                for index in range(0,len(replies)):
                    reps = replies[index].xpath("./ul/li")

                    if len(reps) > 0:
                        for rep in reps:
                            
                            each_rep = {}

                            post["post_comment"].append(each_rep.xpath(".//div[@class='ecm0bbzt e5nlhep0 a8c37x1j']//text()"))



            with open( "./posts/json/group/post_" + post["post"] + '.json', 'w+') as jsonfile:
                json.dump(post, jsonfile, ensure_ascii=False)
        
        # break