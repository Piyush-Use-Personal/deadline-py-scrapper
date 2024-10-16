import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Union
from .abstract import AbstractSource
# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")
class Vulture(AbstractSource):
    def __init__(self) -> None:
        self.domain = "https://www.vulture.com"
        
    def process(self, url: str) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Main method to process the given URL.
        Retrieves primary content, extracts stories, processes child links,
        merges results, and converts to JSON format.
        """
        stories = []
        firstPageSoup = self.get_primary_content(url)
        if firstPageSoup:
            stories = self.get_stories(firstPageSoup)
            parent_links = [story['url'] for story in stories]
            detailed_stories = self.process_children(parent_links)
        result = self.merge_lists_by_key(detailed_stories, stories, 'url')
        return self.to_json(result)
    def get_primary_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetches and parses the primary content from the given URL.
        Returns a BeautifulSoup object or None if the request fails.
        """
        logger.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            logger.error(f"Failed to retrieve the page: {response.status_code}")
            return None
    def get_stories(self, soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
        """
        Extracts story data from the given BeautifulSoup object.
        Returns a list of dictionaries with story details.
        """
        logger.info("Getting all stories")
        stories = []
        story_elements = soup.find_all('li', class_='article')
        for story in story_elements:
            story_data = {}
            # Extract title and URL
            title_element = story.find('div', class_='main-article-content')
            if title_element and title_element.find('a'):
                story_data['title'] = title_element.find('a').get_text(strip=True)
                story_data['url'] = title_element.find('a').get('href')

            # Extract image URL
            image_element = story.find('div', class_='article-img-wrapper').find("img")
            if image_element:
                story_data['thumbnail'] = image_element.get('src')
            stories.append(story_data)
        return stories
    
    def process_children(self, parent_links: List[str]) -> List[Dict[str, Optional[str]]]:
        """
        Processes each child link to extract detailed content.
        Returns a list of dictionaries with detailed story content.
        """
        processed_contents = []
        for url in parent_links:
            logger.info(f"Processing link: {url}")
            content = self.get_primary_content(url)
            if content:
                title = self.get_headline(content)
                child_content = self.get_content(content)
                banner = self.get_banner_image(content)
                categories = self.get_categories(content)
                # date = self.get_date(content)
                author = self.get_author(content)
                author_link = self.get_author_link(content)
                processed_content = {
                    "title": title,
                    "content": child_content,
                    # "date": date,
                    "url": url,
                    "banner": banner,
                    "categories": categories,
                    "author_name": author,
                    "author_url": author_link,
                }
                processed_contents.append(processed_content)
        return processed_contents
    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find('h1', class_='headline-primary')
        if title_element:
            return title_element.get_text(strip=True)
        return None
    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        heading_image = soup.find('img', class_="lede-image")
        if heading_image:
            banner_image = heading_image.get('src')
            if banner_image:
                return banner_image
            return None
        return None
    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        elements = soup.find('div', class_='article-content')
        for child in elements.children:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                child_contents.append(child.get_text(strip=True))
        return child_contents
    def get_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author name from the given BeautifulSoup object.
        Returns the author's name as a string or None if not found.
        """
        logger.info("Getting author")
        author_element = soup.find('div', class_="main-author")
        if author_element:
            author_link = author_element.find('a')
            return author_link.get_text(strip=True)
        return None
        
    def get_author_link(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author link URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting author link")
        author_element = soup.find('div', class_="main-author")
        if author_element:
            author_link = author_element.find('a')
            if author_link:
                return author_link.get('href')
        return None
    
    def get_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the publication date from the given BeautifulSoup object.
        Returns the date as a string or None if not found.
        """
        logger.info("Getting date")
        date_element = soup.find('div', class_="cb-date")
        if date_element:
            return date_element.find('time').get_text(strip=True)
        return None
    def get_categories(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts categories from the given BeautifulSoup object.
        Returns a list of category names.
        """
        logger.info("Getting categories")
        categories = []
        main_content = soup.find('ul', class_="tags-list")
        if main_content:
            a_tags = main_content.findAll('a')
            for a_tag in a_tags:
                categories.append(a_tag.get_text(strip=True))
        return categories
    
    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
        """
        Converts the list of story objects into JSON format.
        Adds additional metadata such as captured date and time.
        """
        json_list = []
        captured_date, captured_time = self.get_current_date_and_time()
        
        for obj in objects:
            publish_date, publish_time = self.parse_datetime(obj.get('date'))
            json_list.append({
                "source": 'vulture',
                "sourceIconURL": 'vulture',
                "sourceSection": ",".join(obj.get("categories", [])),
                "title": obj.get("title", ""),
                "subtitle": obj.get("tagline", ""),
                "content": obj.get("content", ""),
                "author": obj.get("author_name", ""),
                "urlArticle": obj.get("url", ""),
                "urlBannerImage": obj.get("banner", ""),
                "urlThumbnailImage": obj.get("thumbnail", ""),
                
                "publishedDate": publish_date,
                "publishedTime": publish_time,
                "capturedDate": captured_date,
                "capturedTime": captured_time
            })
        
        return json_list