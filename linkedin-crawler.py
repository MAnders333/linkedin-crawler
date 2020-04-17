import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as soup
import time
import random


class LinkedInCrawler():
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)
        self.links_to_visit = []
        self.links_visited = []
        print(f"Bot initialized.\nConnected to {self.url}")

    def authentification(self):
        # Get email and password from environment
        self.email = os.environ.get("LINKEDIN_EMAIL")
        self.pw = os.environ.get("LINKEDIN_PW")

        # Send email address to email field
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "username")))
        email_element = self.driver.find_element_by_id("username")
        email_element.send_keys(self.email)

        # Send password to password field
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "password")))
        password_element = self.driver.find_element_by_id("password")
        password_element.send_keys(self.pw)

        # Click submit button
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button")))
        submit_element = self.driver.find_element_by_css_selector("button")
        submit_element.click()

        # Wait until screen is sufficiently loaded
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "mynetwork-tab-icon")))
        print("Successfully logged in.")

    def crawl(self):
        # First fill links_to_visit to start while loop
        self.goToMyNetwork()
        self.getPYMKLinks()
        print(f"First profiles to visit: {len(self.links_to_visit)}")

        # While links_to_visit is not empty, visit profiles and append additional profiles found
        while len(self.links_to_visit) > 0:
            # Visit and load first page in links_to_visit
            time.sleep(random.uniform(5, 10))
            self.driver.get(self.links_to_visit[0])
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pv-top-card-section__name.inline.t-24.t-black.t-normal")))

            # Register visited link in links_visited and remove it from links_to_visit
            self.links_visited.append(self.links_to_visit[0])
            self.links_to_visit.pop(0)

            # Appends new links on page visited to links_to_visit
            self.getBrowseLinks()

            # If the list is empty, try new links from my network route
            if len(self.links_to_visit) == 0:
                self.goToMyNetwork()
                self.getPYMKLinks()

            print(
                f"{len(self.links_visited)} visited / {len(self.links_to_visit)} queued")

    def goToMyNetwork(self):
        # Go to my network route
        my_network_element = self.driver.find_element_by_id(
            "mynetwork-tab-icon")
        my_network_element.click()
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-launchpad-scroll-anchor=pymk]")))

    def getPYMKLinks(self):
        # Find all PYMK links and append them to links_to_visit
        page_source = self.driver.page_source
        page_html = soup(page_source, "html.parser")
        rel_links = [rel_link.get('href') for rel_link in page_html.findAll(
            "a", {"data-control-name": "pymk_profile", "class": "discover-person-card__link ember-view"})]
        self.appendLinks(rel_links)

    def getBrowseLinks(self):
        # Find all browse links and append them to links_to_visit
        page_source = self.driver.page_source
        page_html = soup(page_source, "html.parser")
        rel_links = [rel_link.get('href') for rel_link in page_html.findAll(
            "a", {"data-control-name": "browsemap_profile", "class": "pv-browsemap-section__member ember-view"})]
        self.appendLinks(rel_links)

    def appendLinks(self, rel_links):
        # rel_links must be an iterable object
        # Appends relative links to links_to_visit
        for rel_link in rel_links:
            full_link = "https://www.linkedin.com" + rel_link
            if full_link not in self.links_visited:
                self.links_to_visit.append(full_link)

    def close(self):
        self.driver.close()


def main():
    bot = LinkedInCrawler("https://www.linkedin.com/login")
    bot.authentification()
    bot.crawl()
    bot.close()


if __name__ == "__main__":
    main()
