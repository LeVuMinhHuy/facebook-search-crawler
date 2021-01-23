# facebook-splash-scraper
Facebook Scraper Using Scrapy-Splash - Huỳnh Ngọc Thiện


## Concept Demonstration

### Step 1: Scrape cookies for loggin session

We will use the first spider to read facebook account set up by users in settings.py to send splash request login to Facebook and retrieve the cookies to store into each cookies json files. This will help later requests avoid multiple login times since each Splash requests is an independent session with customizable headers(which allow us to input previous cookies to keep login session)

![Scrape cookies for loggin session](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/first_spider.png)

### Step 2: Scrape posts links in groups

After getting cookies json files, the second spider will choose one of the cookies (which is not temporarily blocked seeing post by facebook) to be its headers. Next, it will base on the setting groups and number of scroll in the settings.py (setup by user) to crawl posts links and store whole groups pages into groups html files and from there, the python script will extract xpath to get information that users need to store into each groups json files.

![Scrape posts links in groups](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/second_spider.png)

### Step 3: Scrape each post in posts links

Using the groups json files generated in the previous step, the third spider will send Splash request to get the whole post page html and store into post html files. These files once again will be parse by lxml in order to be extracted using xpath to get information base on rules of users. In the end, the output will be posts json files contain information that users. (In this step, the python n script to parse xpath had been separated into a different file since there are a lot of informaiton to be extracted and I think it is better to splice the code for better management and maintanance)

![Scrape each post in posts links](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/third_spider.png)

## Instruction Demonstration

### Preparation

1. Install requirements.txt

```
    pip3 / pip install -r requirements.txt
```

2. Install / Run Splash-NordVPN docker

**Please remember to replace [ACC] and [PWD] with your own NordVPN account**

For further customize NordVPN options, please visit the following [link](https://github.com/azinchen/nordvpn)

Acc: robert.hill1996@gmail.com

Pwd: Mach1n3h3ad

Run NordVPN First

```
sudo docker run -ti --rm --name nordvpn --cap-add=NET_ADMIN --device /dev/net/tun -p 8050:8050 -e NETWORK=192.168.1.0/24 -e USER=[ACC] -e PASS=[PWD] -e RANDOM_TOP="20" -e RECREATE_VPN_CRON="0 12 * * *" -e COUNTRY=Vietnam -e CATEGORY='Standard VPN Servers' -e PROTOCOL=openvpn_udp -d azinchen/nordvpn
```

Run Splash After NordVPN

```
sudo docker run -ti --name splash --restart=always --net=container:nordvpn -d scrapinghub/splash --max-timeout 3600
```

**Remember to always run the above commands or setup it automatically run whenever docker is on before starting running the crawler**

To debug Splash request, please run:

```
docker logs --follow splash
```

### Execution

First open terminal and get into directory facebook_splash_scraper

1. Scrape cookies for loggin session

Run the following code:

```
scrapy crawl facebook_login
```

If the process is successfull, the terminnal will usually print out these lines (for all three spiders):

![Scrape each post in posts links](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/success.png)

The result we will get is the cookies json files:

![These files contain cookie of logged session](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/cookies_file.png)

![Inside cookie files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/cookies.png)

2. Scrape posts links in groups

Run the following code:

```
scrapy crawl facebook_links
```

The result we will get is the groups html and json files:

![Groups Files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/groups_file.png)

![Groups HTML Files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/groups_html.png)

![Groups JSON Files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/groups_json.png)

3. Scrape posts links in groups

Run the following code:

```
scrapy crawl facebook_posts
```

The result we will get is the posts html files:

![Posts HTML Files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/posts_html_files.png)

![Posts HTML](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/posts_html.png)

Run the next code:

```
python3 / python post_extract_xpath.py
```

The result we will get is the final result we want (posts json files with all the information users need):

![Posts JSON Files](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/posts_json_files.png)

![Posts JSON](https://github.com/WhiteWolf21/facebook_splash_scraper/blob/master/readme_images/posts_json.png)

### For further unnderstanding

- [Scrapy](https://docs.scrapy.org/en/latest/)
- [Splash](https://splash.readthedocs.io/en/stable/)
- [Lua](https://www.lua.org/docs.html)

And reading code comments in each python files

### Next steps...

Currently, the tool is being improving by me and therefore, I backup some for later if I try something and it cause failure. Moreover, if you guy see this project is potential, feel free to collaborate with me to contribute and make it better by poiting out errors in codes and execution steps as well as developing more features or fixing some bug.

# Thank You Everyone Very Much For Spending Time Looking Through This Project !!!


