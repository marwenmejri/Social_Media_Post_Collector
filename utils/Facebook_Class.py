from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv


def check_exists_by_css_selector(css_selector, driver):
    try:
        driver.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    return True


class Facebook:

    def __init__(self, driver, username, password, keyword):
        self.driver = driver
        self.username = username
        self.password = password
        self.keyword = keyword

    def sign_in(self):
        self.driver.get(url='https://m.facebook.com/')
        # Accept Cookies
        WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        # target username
        target_username = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        target_password = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                           "input[name='pass']")))

        # enter username and password
        target_username.clear()
        target_username.send_keys(self.username)
        target_password.clear()
        target_password.send_keys(self.password)

        # target the login button and click it
        submit = self.driver.find_element_by_xpath('//*[@id="login_form"]/ul/li[3]/input')
        submit.click()
        # We are logged in!

    def scrap_all_facebook_posts(self):
        data = []
        # Search
        search = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[name='Search']")))
        search.click()

        # search button
        target_search = self.driver.find_element(By.CSS_SELECTOR, "input[id='main-search-input']")
        target_search.clear()
        target_search.send_keys(self.keyword)

        # Target posts sections
        root = self.driver.find_element(By.CSS_SELECTOR, "div[id='u_1o_27_DL']")
        target_posts = root.find_element(By.TAG_NAME, "a")[1]
        target_posts.click()

        posts_root = self.driver.find_element(By.CSS_SELECTOR, "div[class='_45fx _4d7h _1e0o']")
        posts = posts_root.find_elements(By.CSS_SELECTOR, "div[class='story_body_container']")
        for post in posts:
            post_text_root = post.find_element(By.CSS_SELECTOR, "div[class='_5rgt _5nk5 _5wnf _5msi']")
            post_texts = post_text_root.find_elements(By.TAG_NAME, 'p')
            post_text = [_.text for _ in post_texts]

            post_img_root = post.find_element(By.CSS_SELECTOR, "a[class='_39pi _1mh-']")
            post_img = post_img_root.get_attribute("href")

            data["post_txt"] = post_text
            data["post_image"] = post_img

        return data


if __name__ == '__main__':
    load_dotenv('../.env')
    USERNAME = os.getenv('FACEBOOK_USERNAME')
    PASSWORD = os.getenv('FACEBOOK_PASSWORD')

    option = webdriver.ChromeOptions()
    # option.add_argument("--headless")
    option.add_argument("--host-resolver-rules=MAP www.google-analytics.com 127.0.0.1")
    option.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/66.0.3359.181 Safari/537.36')
    DRIVER = webdriver.Chrome('../chromedriver.exe', options=option)

    facebook = Facebook(driver=DRIVER, username=USERNAME, password=PASSWORD, keyword='Python')

    all_posts = facebook.scrap_all_facebook_posts()
