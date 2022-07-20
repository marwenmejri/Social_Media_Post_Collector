from utils.Instagram_Class import Instagram
from utils.Facebook_Class import Facebook

from selenium import webdriver
from pymongo import MongoClient
import os
from dotenv import load_dotenv


def main(keyword, path):
    load_dotenv('../.env')
    insta_username = os.getenv('INSTAGRAM_USERNAME')
    insta_password = os.getenv('INSTAGRAM_PASSWORD')

    fb_username = os.getenv('FACEBOOK_USERNAME')
    fb_password = os.getenv('FACEBOOK_PASSWORD')

    option = webdriver.ChromeOptions()
    # option.add_argument("--headless")
    option.add_argument("--host-resolver-rules=MAP www.google-analytics.com 127.0.0.1")
    option.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/66.0.3359.181 Safari/537.36')
    driver = webdriver.Chrome(path, options=option)

    instagram = Instagram(driver=driver, username=insta_username, password=insta_password, keyword=keyword)
    all_insta_posts = instagram.scrap_all_instagram()

    facebook = Facebook(driver=driver, username=fb_username, password=fb_password, keyword=keyword)

    all_fb_posts = facebook.scrap_all_facebook_posts()

    # MongoDB connection:

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    connexion_str = "mongodb+srv://marwenmej:20759232@test_tech.mongodb.net/"
    client = MongoClient(connexion_str)
    db = client["facebook"]
    fb_col = db["fb_posts"]
    insta_col = db["insta_posts"]

    # insert the list of posts
    fb_col.insert_many(all_fb_posts)
    insta_col.insert_many(all_insta_posts)

    # Show an example of each social media collection
    print(fb_col.find_one())
    print(insta_col.find_one())


if __name__ == '__main__':
    main(keyword="python", path=r"../chromedriver.exe")
