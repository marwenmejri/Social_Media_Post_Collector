from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import pandas as pd
import random
import pickle


def check_exists_by_css_selector(css_selector, driver):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    return True


class Instagram:

    def __init__(self, driver, username, password, keyword):
        self.driver = driver
        self.username = username
        self.password = password
        self.keyword = keyword

    def sign_in(self):
        self.driver.get(url='https://www.instagram.com/')
        # target username
        target_username = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        target_password = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

        # enter username and password
        target_username.clear()
        target_username.send_keys(self.username)
        target_password.clear()
        target_password.send_keys(self.password)

        # target the login button and click it
        submit = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit.click()
        # We are logged in!

        not_now = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Plus tard")]')))
        not_now.click()

    def google_scrap(self):
        url = 'https://google.com/search?q=' + '"' + self.keyword + '"' + "%20site:instagram.com/p/"
        self.driver.get(url)
        time.sleep(random.randint(1, 10))
        results_length = 0
        results = []
        while True:
            root = self.driver.find_element(By.CSS_SELECTOR, "div[id='search']")
            # root = root.find_element(By.CSS_SELECTOR, "div[class='v7W49e']")
            links = root.find_elements(By.CSS_SELECTOR, "div[class='g Ww4FFb tF2Cxc']")
            links2 = root.find_elements(By.CSS_SELECTOR, "div[class='hlcw0c']")
            links = links + links2

            for link in links:
                a = link.find_element(By.TAG_NAME, "a")
                url = a.get_attribute("href")
                if "%" in url:
                    continue
                else:
                    results.append(url)

            results = pd.Series(results)
            results = results.drop_duplicates()
            results = results.to_list()

            if len(results) == results_length:
                break

            if check_exists_by_css_selector("span[class='SJajHc NVbCr']", self.driver):
                suivant = self.driver.find_elements(By.CSS_SELECTOR, "span[class='SJajHc NVbCr']")[-1]
                suivant.click()
                time.sleep(5)
                results_length = len(results)
                if results_length > 10:
                    print(results_length)
                    break

        return results

    def instagram_scrap(self, url):
        self.driver.get(url)
        time.sleep(2)
        data = {}
        max_taille = 24
        taille = 12
        commentaires = []

        post_body = self.driver.find_element(By.CSS_SELECTOR, "div[class='_aa6b _aa6d']")
        post_text = post_body.find_element(By.CSS_SELECTOR, "div[class='_a9zn _a9zo']")
        post_text = post_text.find_element(By.TAG_NAME, 'span').text
        # print(post_text.text)
        post_image = post_body.find_element(By.CSS_SELECTOR, "div[class='_aagv']")
        post_image = post_image.find_element(By.TAG_NAME, 'img').get_attribute('src')

        while taille < max_taille:
            allcomments = self.driver.find_elements_by_class_name('Mr508')
            taille = len(allcomments)
            try:
                load_more_comments_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div/ul/li/div/button/span"))
                )
                load_more_comments_element.click()
                time.sleep(5)
            except:
                print('No more comments')
            allcomments_max = self.driver.find_elements_by_class_name('Mr508')
            max_taille = len(allcomments_max)

        for comment in allcomments_max:
            element = comment.find_elements_by_class_name('C4VMK')[0]
            comment_text = element.find_elements_by_tag_name("span")[1].text
            commentaires.append(comment_text)

        data["post_txt"] = post_text
        data["comments"] = commentaires
        data["post_image"] = post_image

        return data

    def scrap_all_instagram(self):
        posts = []
        urls = self.google_scrap()
        j = 0
        for url in urls:
            j += 1
            cookie_file_name = "cookies_instagram.pkl"
            try:
                self.driver.get(url)
                time.sleep(random.randint(1, 10))
                cookies = pickle.load(open(cookie_file_name, "rb"))
                i = 0
                while i < len(cookies):
                    self.driver.add_cookie(cookies[i])
                    time.sleep(random.randint(1, 10))
                    self.driver.get(url)
                    time.sleep(random.randint(1, 10))
                    i += 1
                    if check_exists_by_css_selector("button[class='sqdOP  L3NKy   y3zKF     ']", driver=self.driver):
                        pass
                    else:
                        i = len(cookies)
                post = self.instagram_scrap(url=url)
                posts.append(post)
            except FileNotFoundError:
                self.sign_in()
                time.sleep(random.randint(1, 10))
                self.driver.get(url)
                # Save cookies
                pickle.dump(self.driver.get_cookies(), open(cookie_file_name, "wb"))

            time.sleep(3)
        self.driver.quit()

        return posts


if __name__ == '__main__':
    load_dotenv('../.env')
    USERNAME = os.getenv('INSTAGRAM_USERNAME')
    PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

    option = webdriver.ChromeOptions()
    # option.add_argument("--headless")
    option.add_argument("--host-resolver-rules=MAP www.google-analytics.com 127.0.0.1")
    option.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/66.0.3359.181 Safari/537.36')
    DRIVER = webdriver.Chrome('../chromedriver.exe', options=option)

    instagram1 = Instagram(driver=DRIVER, username=USERNAME, password=PASSWORD, keyword='Jacques Chirac')

    all_posts = instagram1.scrap_all_instagram()
