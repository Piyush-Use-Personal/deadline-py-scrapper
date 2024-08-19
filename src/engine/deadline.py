import requests
from bs4 import BeautifulSoup
import logging
from .abstract import AbstractSource

logging.basicConfig(level=logging.INFO)

class Deadline(AbstractSource):
    def __init__(self):
        self.parentLinkClassName = "c-title__link"
        self.childContentClassName = "a-content"
        self.childExcludeClassName = "injected-related-story"
        self.titleClassName = "c-title"
        self.authorClassName = "pmc-u-margin-tb-00 pmc-u-font-size-14"
        self.dateClassName = "pmc-u-color-grey-medium-dark"
        self.categoriesClassName = "o-nav__list-item"
        self.categoryLinkClassName = "c-nav-link"

    def process(self, url):
        final_contents = []
        soup = self.getPrimaryContent(url)
        if soup:
            parent_links = self.getChildLinks(soup)
            processed_contents = self.processChildren(parent_links)
            final_contents.extend(processed_contents)
        return final_contents

    def getPrimaryContent(self, url):
        logging.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            logging.error(f"Failed to retrieve the page: {response.status_code}")
            return None

    def getChildLinks(self, soup):
        logging.info("Getting parent links")
        parent_links = []
        links = soup.find_all('a', class_=self.parentLinkClassName)
        for link in links:
            parent_links.append(link.get('href'))
        return parent_links

    def processChildren(self, parent_links):
        processed_contents = []
        for link in parent_links:
            logging.info(f"Processing link: {link}")
            content = self.getPrimaryContent(link)
            if content:
                title = self.getHeadline(content)
                child_content = self.getContent(content)
                author = self.getAuthor(content)
                date = self.getDate(content)
                categories = self.getCategories(content)
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "author": author,
                    "date": date,
                    "categories": categories,
                    "link": link
                }
                processed_contents.append(processed_content)
        return processed_contents

    def getHeadline(self, soup):
        logging.info("Getting title")
        title_element = soup.find('h1', class_=self.titleClassName)
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def getContent(self, soup):
        logging.info("Getting child content")
        child_contents = []
        elements = soup.find_all('div', class_=self.childContentClassName)
        for element in elements:
            if self.childExcludeClassName not in element.get('class', []):
                text = element.get_text(strip=True)
                child_contents.append(text)
        return child_contents

    def getAuthor(self, soup):
        logging.info("Getting author")
        author_element = soup.find('p', class_=self.authorClassName)
        if author_element:
            return author_element.get_text(strip=True)
        return None
        
    def getDate(self, soup):
        logging.info("Getting date")
        date_element = soup.find('time', class_=self.dateClassName)
        if date_element:
            return date_element.get_text(strip=True)
        return None

    def getCategories(self, soup):
        logging.info("Getting categories")
        categories = []
        nav_items = soup.find_all('li', class_=self.categoriesClassName)
        for item in nav_items:
            a_tag = item.find('a', class_=self.categoryLinkClassName)
            if a_tag:
                categories.append(a_tag.get_text(strip=True))
        return categories