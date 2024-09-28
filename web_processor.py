import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

class WebProcessor:

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
        links = soup.find_all('a', class_="c-title__link")
        for link in links:
            parent_links.append(link.get('href'))
        return parent_links

    def processLink(self, parent_links):
        processed_contents = []
        for link in parent_links:
            logging.info(f"Processing link: {link}")
            content = self.getPrimaryContent(link)
            if content:
                title = self.getTitle(content)
                child_content = self.getChildContent(content)
                author = self.getAuthor(content)
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "author": author
                }
                processed_contents.append(processed_content)
        return processed_contents

    def getTitle(self, soup):
        logging.info("Getting title")
        title_element = soup.find('h1', class_="c-title")
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def getChildContent(self, soup):
        logging.info("Getting child content")
        child_contents = []
        elements = soup.find_all('div', class_="a-content")
        for element in elements:
            if "injected-related-story" not in element.get('class', []):
                text = element.get_text(strip=True)
                child_contents.append(text)
        return child_contents

    def getAuthor(self, soup):
        logging.info("Getting author")
        author_element = soup.find('p', class_="pmc-u-margin-tb-00 pmc-u-font-size-14")
        if author_element:
            return author_element.get_text(strip=True)
        return None
    
    def process(self, url):
        final_contents = []
        soup = self.getPrimaryContent(url)
        if soup:
            parent_links = self.getParentLinks(soup)
            processed_contents = self.processLink(parent_links)
            final_contents.extend(processed_contents)
        return final_contents
