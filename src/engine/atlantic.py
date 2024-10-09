import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Union

from .abstract import AbstractSource

# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")

class Atlantic(AbstractSource):
    def __init__(self) -> None:
        self.domain = "https://theatlantic.com"

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

        story_elements = soup.find_all('article', class_='LandingRiver_promoItem__SLYUT')
        for story in story_elements:
            story_data = {}

            # Extract title and URL
            title_element = story.find('a', class_='LandingRiver_titleLink__nUImQ')
            if title_element and title_element.find('span'):
                story_data['title'] = title_element.find('span').get_text(strip=True)
                story_data['url'] = title_element.get('href')

            # Extract author
            author_element = story.find('p', class_='LandingMetadata_root__qrlUA')
            if author_element and author_element.find('a'):
                author_name = author_element.find('a').get_text(strip=True)
                author_url = author_element.find('a').get('href')
                story_data['author_name'] = author_name
                story_data['author_url'] = author_url

            # Extract publication time
            time_element = story.find('time', class_='LandingMetadata_datePublished__iRPUc')
            print(time_element)
            if time_element:
                story_data['time'] = time_element.get('datetime')

            # Extract image URL
            image_element = story.find('img', class_='LandingRiver_image__VWDpl')
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
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "url": url,
                    "banner": banner,
                    "categories": categories,
                }
                processed_contents.append(processed_content)
        return processed_contents

    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find('h1', class_='ArticleTitle_root__VrZaG')
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        heading_image = soup.find('img', class_="Image_root__XxsOp ArticleLeadArt_image__HZS4B")
        if heading_image:
            return heading_image.get('src')
        return None

    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        elements = soup.find('section', class_='ArticleBody_root__2gF81')
        for child in elements.children:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                child_contents.append(child.get_text(strip=True))
        return child_contents

    def get_categories(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts categories from the given BeautifulSoup object.
        Returns a list of category names.
        """
        logger.info("Getting categories")
        categories = []
        nav_items = soup.find_all('a', class_="ArticleRubric_link__nl9hy")
        for item in nav_items:
            categories.append(item.get_text(strip=True))
        return categories
    
    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
        """
        Converts the list of story objects into JSON format.
        Adds additional metadata such as captured date and time.
        """
        json_list = []
        captured_date, captured_time = self.get_current_date_and_time()
        
        for obj in objects:
            publish_date, publish_time = self.extract_date_time_from_iso(obj.get('time'))
            json_list.append({
                "source": 'atlantic',
                "sourceIconURL": 'atlantic',
                "sourceSection": obj.get("categories", [])[0] if obj.get("categories") else "",
                "title": obj.get("title", ""),
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
