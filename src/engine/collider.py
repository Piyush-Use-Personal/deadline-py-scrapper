from datetime import datetime
from typing import List, Dict, Union, Optional
from .abstract import AbstractSource
from loguru import logger
import sys
import requests
from bs4 import BeautifulSoup



class Collider(AbstractSource):
    def __init__(self):
        self.domain = "https://www.collider.com"

    def process(self, url: str) -> List[Dict[str, Union[str, List[str]]]]:
        soup = self.get_primary_content(url)
        if soup:
            stories = self.get_stories(soup)
            parent_links = [story["url"] for story in stories]
            detailed_stories = self.process_children(parent_links)
            result = self.merge_lists_by_key(detailed_stories, stories, "url")
            return self.to_json(result)
        return []

    def get_primary_content(self, url: str) -> Optional[BeautifulSoup]:
        logger.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
        else:
            logger.error(f"Failed to retrieve the page: {response.status_code}")
            return None

    def process_children(
        self, parent_links: List[str]
    ) -> List[Dict[str, Optional[str]]]:
        logger.info("Processing child elements")
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
        
        # Move return statement outside the for loop
        return processed_contents



    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find("h1", class_="article-header-title")
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        heading_image = soup.find("div", class_="heading_image")
        if heading_image:
            return heading_image.find("img").get("src")
        return None

    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        elements = soup.find("div", class_="content-block-regular")
        for child in elements.children:
            if child.name in ["h1", "h2", "h3", "h4", "h5", "h6", "p"]:
                child_contents.append(child.get_text(strip=True))
        return child_contents

    def get_stories(self, soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
        """
        Extracts story data from the given BeautifulSoup object.
        Returns a list of dictionaries with story details.
        """
        logger.info("Getting all stories")
        stories = []
        container = soup.find("div", class_="section-latest-news")
        story_elements = container.find_all("div", class_="display-card")
        for story in story_elements:
            story_data = {}

            # Extract title and URL
            title_element = story.find("h5", class_="display-card-title")
            if title_element and title_element.find("a"):
                story_data["title"] = title_element.find("a").get_text(strip=True)
                story_data["url"] = self.domain + title_element.find("a").get("href")

            # Extract author
            author_element = story.find("div", class_="w-author")
            if author_element:
                author_name = author_element.find("a")
                if author_name:
                    story_data["author_name"] = author_name.get_text(strip=True)
                    story_data["author_url"] = self.domain + author_name.get("href")

            # Extract publication time
            time_element = story.find("time", class_="display-card-date")
            if time_element:
                story_data["time"] = time_element.get("datetime")

            # Extract category
            category_element = story.find("div", class_="w-display-card-category")
            if category_element and category_element.find("a"):
                story_data["category"] = category_element.find("a").get_text(strip=True)

            # Extract thumbnail image URL from <source> tags
            thumbnail_image = ""
            source_elements = story.find_all("source")
            for source in source_elements:
                if source.get("srcset"):
                    thumbnail_image = source.get("srcset")
                    break  # Use the first srcset found

            # If no srcset found, fall back to the img tag
            if not thumbnail_image:
                image_element = story.find("img")
                if image_element:
                    thumbnail_image = image_element.get(
                        "data-img-url", image_element.get("src")
                    )

            story_data["thumbnail"] = thumbnail_image
            stories.append(story_data)

        return stories

    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
        """
        Converts the list of story objects into JSON format.
        Adds additional metadata such as captured date and time.
        """
        json_list = []
        captured_date, captured_time = self.get_current_date_and_time()

        for obj in objects:
            # Initialize publish_date and publish_time
            publish_date = ""
            publish_time = ""

            if obj.get("time"):
                publish_date, publish_time = self.extract_date_time_from_iso(
                    obj["time"]
                )

            json_list.append(
                {
                    "source": "screenrant",
                    "sourceIconURL": "screenrant",
                    "sourceSection": obj.get("category", ""),
                    "title": obj.get("title", ""),
                    "content": (
                        obj.get("content", [])
                        if isinstance(obj.get("content"), list)
                        else []
                    ),  # Ensure content is a list
                    "author": obj.get("author_name", ""),
                    "urlArticle": obj.get("url", ""),
                    "link": obj.get("url", ""),
                    "urlBannerImage": obj.get("banner", ""),
                    "urlThumbnailImage": obj.get("thumbnail", ""),
                    "publishedDate": publish_date,
                    "publishedTime": publish_time,
                    "capturedDate": captured_date,
                    "date": captured_date,
                    "capturedTime": captured_time,
                    "categories": [],
                }
            )

        return json_list


# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")
