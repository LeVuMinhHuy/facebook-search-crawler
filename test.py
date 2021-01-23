import json

data = ''

with open('/Users/WhiteWolf21/Documents/GitHub/facebook_splash_scraper/posts/json/post_3741369919263013.json') as json_file:
    data = json.load(json_file)

with open('/Users/WhiteWolf21/Documents/GitHub/facebook_splash_scraper/posts/json/post_3741369919263013.json', 'w+') as json_file:
    json.dump(data, json_file, ensure_ascii=False)
    