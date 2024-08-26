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
        self.bannerImageClassname = "c-figure__image"
        self.storyClassName = "river-story a-archive-grid__story"

    def process(self, url):
        stories = []
        firstPageSoup = self.getPrimaryContent(url)
        if firstPageSoup:
            stories = self.getStories(firstPageSoup)
            parent_links = [story['url'] for story in stories]
            detailed_stories = self.processChildren(parent_links)
        return self.merge_lists_by_key(detailed_stories, stories, 'url')

    def getPrimaryContent(self, url):
        logging.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            logging.error(f"Failed to retrieve the page: {response.status_code}")
            return None

    def getStories(self, soup):
        logging.info("Getting all stories")
        stories = []

        story_elements = soup.find_all('div', class_=self.storyClassName)
        for story in story_elements:
            story_data = {}

            # Extract title and URL
            title_element = story.find('h3', class_='c-title')
            if title_element and title_element.find('a'):
                story_data['title'] = title_element.find('a').get_text(strip=True)
                story_data['url'] = title_element.find('a').get('href')

            # Extract author
            author_element = story.find('p', class_='c-byline')
            if author_element and author_element.find('a'):
                author_name = author_element.find('a').get_text(strip=True)
                author_url = author_element.find('a').get('href')
                story_data['author_name'] = author_name
                story_data['author_url'] = author_url

            # Extract publication time
            time_element = story.find('time')
            if time_element:
                story_data['time'] = time_element.get_text(strip=True)

            # Extract category
            category_element = story.find('ul', class_='a-unstyle-list')
            if category_element and category_element.find('a'):
                story_data['category'] = category_element.find('a').get_text(strip=True)

            # Extract image URL
            image_element = story.find('img', class_='c-figure__image')
            if image_element:
                story_data['thumbnail'] = image_element.get('src')

            stories.append(story_data)

        return stories

    def getChildLinks(self, firstPageSoup):
        logging.info("Getting parent links")
        parent_links = []
        links = firstPageSoup.find_all('a', class_=self.parentLinkClassName)
        for link in links:
            parent_links.append(link.get('href'))
        return parent_links

    def processChildren(self, parent_links):
        processed_contents = []
        for url in parent_links:
            logging.info(f"Processing link: {url}")
            content = self.getPrimaryContent(url)
            if content:
                title = self.getHeadline(content)
                child_content = self.getContent(content)
                author = self.getAuthor(content)
                author_link = self.getAuthorLink(content)
                date = self.getDate(content)
                categories = self.getCategories(content)
                banner = self.getBannerImage(content)
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "author_name": author,
                    "date": date,
                    "categories": categories,
                    "url": url,
                    "banner": banner,
                    "author_url": author_link
                }
                processed_contents.append(processed_content)
        return processed_contents

    def getHeadline(self, soup):
        logging.info("Getting title")
        title_element = soup.find('h1', class_=self.titleClassName)
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def getBannerImage(self, soup):
        logging.info("Getting banner image")
        banner_element = soup.find('img', class_=self.bannerImageClassname)
        if banner_element:
            return banner_element.get('data-lazy-src')
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
            author_link = author_element.find('a')
            if author_link:
                author_name = author_link.find('span').get_text(strip=True)
            return author_name
        return None
        
    def getAuthorLink(self, soup):
        logging.info("Getting author")
        author_element = soup.find('p', class_=self.authorClassName)
        if author_element:
            author_link = author_element.find('a')
            if author_link:
                author_url  = author_link.get('href')
            return author_url 
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