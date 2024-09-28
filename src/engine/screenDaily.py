import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Union
from .abstract import AbstractSource
# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")
class ScreenDaily(AbstractSource):
    def __init__(self) -> None:
        # Initialize class with specific CSS class names for various elements
        self.parentLinkClassName = "bc-title__link"
        self.childContentClassName = "bc-content"
        self.childExcludeClassName = "injected-story"
        self.titleClassName = "bc-title"
        self.authorClassName = "author-class"
        self.dateClassName = "date-class"
        self.categoriesClassName = "categories-class"
        self.categoryLinkClassName = "category-link-class"
        self.bannerImageClassname = "banner-image-class"
        self.storyClassName = "story-class"
        self.domain = "https://www.screendaily.com"
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
        return self.to_jSON(result)
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
        story_elements = soup.find_all('div', class_='spinLayout')
        for story in story_elements:
            story_data = {}
            # Extract title and URL
            title_element = story.find('h2')
            if title_element and title_element.find('a'):
                story_data['title'] = title_element.find('a').get_text(strip=True)
                story_data['url'] = self.domain + title_element.find('a').get('href')
            # Extract image URL
            image_element = story.find('img')
            if image_element:
                story_data['thumbnail'] = image_element.get('src')
            stories.append(story_data)
        return stories
    def get_child_links(self, firstPageSoup: BeautifulSoup) -> List[str]:
        """
        Extracts parent links from the given BeautifulSoup object.
        Returns a list of URLs.
        """
        logger.info("Getting parent links")
        parent_links = []
        links = firstPageSoup.find_all('a', class_=self.parentLinkClassName)
        for link in links:
            parent_links.append(link.get('href'))
        return parent_links
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
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "url": url,
                    "banner": banner,
                }
                processed_contents.append(processed_content)
        return processed_contents
    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find('div', class_='story_title')
        if title_element:
            return title_element.find('h1').get_text(strip=True)
        return None
    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        heading_image = soup.find('div', class_="articleContent")
        if heading_image:
            return heading_image.find('img').get('src')
        return None
    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        elements = soup.find('div', class_='articleContent')
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
        author_element = soup.find('p', class_="byline meta")
        if author_element:
            author_link = author_element.find('a')
            if author_link:
                return author_link.get_text(strip=True)
        return None
        
    def get_author_link(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author link URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting author link")
        author_element = soup.find('p', class_="byline meta")
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
        date_element = soup.find('span', class_="date")
        if date_element:
            return date_element.get_text(strip=True)
        return None
    def get_categories(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts categories from the given BeautifulSoup object.
        Returns a list of category names.
        """
        logger.info("Getting categories")
        categories = []
        nav_items = soup.find_all('li', class_=self.categoriesClassName)
        for item in nav_items:
            a_tag = item.find('a', class_=self.categoryLinkClassName)
            if a_tag:
                categories.append(a_tag.get_text(strip=True))
        return categories
    
    def to_jSON(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
        """
        Converts the list of story objects into JSON format.
        Adds additional metadata such as captured date and time.
        """
        json_list = []
        captured_date, captured_time = self.get_current_date_and_time()
        
        for obj in objects:
            publish_date, publish_time = self.extract_date_time_from_iso(obj.get('time'))
            json_list.append({
                "source": 'screendaily',
                "sourceIconURL": 'screendaily',
                "sourceSection": obj.get("categories", [])[0] if obj.get("categories") else obj.get("category", "") if "category" in obj else "",
                "title": obj.get("title", ""),
                "content": obj.get("content", ""),
                "timePublished": publish_time,
                "datePublished": publish_date,
                "authorName": obj.get("author_name", ""),
                "authorLink": obj.get("author_url", ""),
                "url": obj.get("url", ""),
                "banner": obj.get("banner", ""),
                "timeCaptured": captured_time,
                "dateCaptured": captured_date,
            })
        
        return json_list