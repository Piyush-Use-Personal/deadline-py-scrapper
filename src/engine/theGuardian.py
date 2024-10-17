from datetime import datetime
from typing import List, Dict, Union, Optional
from .abstract import AbstractSource
from loguru import logger
import sys
import requests
from bs4 import BeautifulSoup
from src.engine.utils.getTodayDate import get_today_date


class TheGuardian(AbstractSource):
    def __init__(self):
        self.domain = "https://www.theguardian.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

    def process(self, url: str) -> List[Dict[str, Union[str, List[str]]]]:
        soup = self.get_primary_content(url)
        if soup:
            stories = self.get_stories(soup)
            parent_links = [story["link"] for story in stories]
            detailed_stories = self.process_children(parent_links)
            result = self.merge_lists_by_key(detailed_stories, stories, "link")
            return self.to_json(result)
        return []

    def get_primary_content(self, url: str) -> Optional[BeautifulSoup]:
        logger.info(f"Fetching primary content from {url}")

        response = requests.get(url, headers=self.headers)
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
                # title = self.get_headline(content)
                child_content = self.get_content(content)
                title = self.get_title(content)
                banner = self.get_banner_image(content)
                category = self.get_category(content)
                author = self.get_author(content)
                date_and_time = self.get_date_and_time(content)

                processed_content = {
                    # "title": title,
                    "content": child_content,
                    "author": author,
                    "title": title,
                    "category": [category],
                    "link": url,
                    "banner": banner,
                    "publishedTime": (
                        date_and_time["date_time"]
                        if date_and_time and "date_time" in date_and_time
                        else None
                    ),
                    "publishedDate": (
                        date_and_time["date_time"]
                        if date_and_time and "date_time" in date_and_time
                        else None
                    ),
                }
                processed_contents.append(processed_content)

        # Return after all URLs are processed
        return processed_contents

    def get_title(self, soup: BeautifulSoup):
        logger.info("Getting title")
        title_element = soup.find("h1", class_="dcr-1w6uej9") or soup.find(
            "div", {"data-gu-name": "standfirst"}
        ).find("p")

        if title_element:
            title = title_element.get_text(strip=True)
            return title

    def get_category(self, soup: BeautifulSoup):
        logger.info("Getting category")
        category_element = soup.find("div", class_="breadcrumbs")
        if category_element:
            category = category_element.find("a").get_text(strip=True)
            return category

    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        heading_image = soup.select_one("#img-1 > picture > img")
        if heading_image:
            image = heading_image.get("src")
            return image
        return None

    def get_author(self, soup: BeautifulSoup) -> Optional[str]:
        logger.info("Getting author")
        try:
            author_element = soup.find("a", {"rel": "author"})
            if author_element:
                return author_element.get_text(strip=True)
            return None
        except AttributeError as e:
            logger.error(f"Failed to extract author: {e}")
            return None

    def get_date_and_time(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        logger.info("Getting date and time")
        try:
            # Attempt to find the time tag
            time_tag = soup.find("span", class_="dcr-u0h1qy")
            if not time_tag:
                time_tag = soup.find("div", class_="dcr-1pexjb9")

            if time_tag:
                # Assuming you want to extract text and possibly other attributes
                date_time_info = {
                    "date_time": time_tag.get_text(
                        strip=True
                    ),  # Extract the text from the span
                    # Add other attributes if needed, e.g.:
                    # 'attribute_name': time_tag.get('attribute_name')
                }
                return date_time_info

            # If time_tag is not found, log a warning and return None
            logger.warning("Time tag not found.")
            return None

        except Exception as e:  # Catch all exceptions to provide better error handling
            logger.error(f"Failed to extract date and time: {e}")
            return None

    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        elements = soup.find("section", class_="dcr-vxrady")
        elements = soup.select_one("#maincontent > div")
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

        # parent_UL = soup.find("section", id_=get_today_date())
        today_date = get_today_date()
        parent_section = soup.find("section", {"data-component": today_date})

        if parent_section:
            All_li_tag = parent_section.find("ul", class_="dcr-pnnc7v")
            for story in All_li_tag.find_all("li"):
                story_data = {}

                link = self.domain + story.find("div", class_="dcr-rni59y").find(
                    "a"
                ).get("href")
                story_data["link"] = link

                stories.append(story_data)

        return stories

    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
            json_list = []
            captured_date, captured_time = self.get_current_date_and_time()

            for obj in objects:
                json_list.append(
                    {
                        "source": "theguardian",
                        "sourceIconURL": "theguardian",
                        "sourceSection": ", ".join(
                            str(category) for category in obj.get("category", []) if category is not None
                        ),  # Make sure this returns a string for display purposes
                        "title": obj.get("title", ""),
                        "content": (
                            obj.get("content", []) if isinstance(obj.get("content"), list) else []
                        ),  # Ensure content is a list
                        "author": obj.get("author", ""),
                        "urlArticle": obj.get("link", ""),
                        "link": obj.get("link", ""),
                        "urlBannerImage": obj.get("banner", ""),
                        "urlThumbnailImage": obj.get("banner", ""),
                        "date": obj.get("publishedDate", ""),
                        "categories": [],  # Ensure this is always a list
                        "publishedDate": obj.get("publishedDate", ""),
                        "publishedTime": obj.get("publishedTime", ""),
                        "capturedDate": captured_date,
                        "capturedTime": captured_time,
                    }
                )

            return json_list




# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")
