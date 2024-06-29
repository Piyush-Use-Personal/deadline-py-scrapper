import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

class WebProcessor:
    def __init__(self):
        self.parentLinkClassName = "c-title__link"
        self.childContentClassName = "a-content"
        self.childExcludeClassName = "injected-related-story"

    def getPrimaryContent(self, url):
        logging.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            logging.error(f"Failed to retrieve the page: {response.status_code}")
            return None

    def getParentLinks(self, soup):
        logging.info("Getting parent links")
        parent_links = []
        links = soup.find_all('a', class_=self.parentLinkClassName)
        for link in links:
            parent_links.append(link.get('href'))
        return parent_links

    def processLink(self, parent_links):
        child_contents = []
        for link in parent_links:
            logging.info(f"Processing link: {link}")
            content = self.getPrimaryContent(link)
            if content:
                child_content = self.getChildContent(content)
                child_contents.extend(child_content)
        return child_contents

    def getChildContent(self, soup):
        logging.info("Getting child content")
        child_contents = []
        elements = soup.find_all('div', class_=self.childContentClassName)
        for element in elements:
            if self.childExcludeClassName not in element.get('class', []):
                text = element.get_text(strip=True)
                child_contents.append(text)
        return child_contents

    def process(self, url):
        final_contents = []
        soup = self.getPrimaryContent(url)
        if soup:
            parent_links = self.getParentLinks(soup)
            child_contents = self.processLink(parent_links)
            final_contents.extend(child_contents)
        return final_contents
