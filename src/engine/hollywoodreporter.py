import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Union

from .abstract import AbstractSource

# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")

class HollywoodReporter(AbstractSource):

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

        # Find all story containers
        story_elements = soup.find_all('div', class_='story')

        for story in story_elements:
            story_data = {}

            # Extract title and URL
            title_element = story.find('h3', class_='c-title')
            if title_element and title_element.find('a'):
                story_data['title'] = title_element.find('a').get_text(strip=True)
                story_data['url'] = title_element.find('a').get('href')

            # Extract author
            author_element = story.find('div', class_='c-tagline')
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
            category_element = story.find('span', class_='c-span')
            if category_element and category_element.find('a'):
                story_data['category'] = category_element.find('a').get_text(strip=True)

            # Extract image URL
            image_element = story.find('img', class_='c-lazy-image__img')
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
                tagline = self.get_tagline(content)
                child_content = self.get_content(content)
                author = self.get_author(content)
                author_link = self.get_author_link(content)
                date = self.get_date(content)
                categories = self.get_categories(content)
                banner = self.get_banner_image(content)
                processed_content = {
                    "title": title,
                    "content": child_content,
                    "author_name": author,
                    "date": date,
                    "categories": categories,
                    "url": url,
                    "banner": banner,
                    "author_url": author_link,
                    "tagline": tagline
                }
                processed_contents.append(processed_content)
        return processed_contents

    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find('h1', class_="article-title")
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def get_tagline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting tagline")
        title_element = soup.find('p', class_="article-excerpt")
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        banner_element = soup.find('img', class_="c-lazy-image__img")
        if banner_element:
            return banner_element.get('data-lazy-src')
        return None
    
    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content, excluding social media and other unwanted sections.
        """
        logger.info("Getting child content")
        
        # Find all content blocks
        article_content = soup.find_all('div', class_='a-content')
        
        # Exclude social media sections by skipping divs with class 'a-article-grid__social'
        filtered_content = []
        for content in article_content:
            social_section = content.find('div', class_='a-article-grid__social')
            if social_section:
                # Remove the social section from the content if it exists
                social_section.extract()
            
            # Add the remaining content to the filtered content list
            filtered_content.append(content.get_text(strip=True))

        return filtered_content

    def get_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author name from the given BeautifulSoup object.
        Returns the author's name as a string or None if not found.
        """
        logger.info("Getting author")
        # Find the specific author section
        author_section = soup.find('div', class_='a-article-grid__author')

        # Look for the anchor tag within the author section
        if author_section:
            author_tag = author_section.find('a', href=True)  # Ensure it's an anchor with href
            if author_tag:
                return author_tag.get_text(strip=True)
        return None
        
    def get_author_link(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author link URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting author link")
        author_section = soup.find('div', class_='a-article-grid__author')
        if author_section:
            author_link = author_section.find('a')
            if author_link:
                return author_link.get('href')
        return None
    
    def get_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the publication date from the given BeautifulSoup object.
        Returns the date as a string or None if not found.
        """
        logger.info("Getting date")
        author_section = soup.find('div', class_='a-article-grid__author')
        if author_section:
            date_element = author_section.find('time')
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
        nav_items = soup.find_all('li')
        for item in nav_items:
            a_tag = item.find('a', class_="")
            if a_tag:
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
            publish_date, publish_time = self.extract_date_time(obj.get('date'))
            json_list.append({
                "source": 'hollywoordreporter',
                "sourceIconURL": 'hollywoordreporter',
                "sourceSection": obj.get("categories", [])[0] if obj.get("categories") else "",
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
