from datetime import datetime
from typing import List, Dict, Union, Optional
from .abstract import AbstractSource
from loguru import logger
import sys
import requests
from bs4 import BeautifulSoup


class IndieWire(AbstractSource):
    def __init__(self):
        self.domain = "https://www.indiewire.com/"

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
                    "link": url,
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
        heading_image = soup.find("div", {"data-alias": "image__inner-img"})
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
        elements = soup.find("div", {"data-alias": "gutenberg-content__content"})
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

        parent_div = soup.find_all("div", {"data-alias": "card__inner"})

        if parent_div:
            for story in parent_div:
                story_data = {}

                outer_div = story.find("div", {"data-alias": "card__main"})
                if outer_div is not None:
                    category_div = outer_div.find("div", {"data-alias": "card__kicker"})
                    if category_div is not None:
                        category = category_div.get_text(strip=True)
                        story_data["category"] = [category]

                title_div = story.find("div", {"data-alias": "card__card-title"})
                if title_div is not None:
                    title = title_div.get_text(strip=True)
                    if title:  # Check if title is not empty
                        story_data["title"] = title

                link_div = story.find("div", {"data-alias": "card__card-title"}).find(
                    "a"
                )
                if link_div:
                    story_data["link"] = link_div.get("href")

                author_div = story.find("div", {"data-alias": "byline__text-wrapper"})
                if author_div is not None:
                    author_span = author_div.find("span")
                    if author_span is not None:
                        story_data["author"] = author_span.get_text(strip=True)

                time_element = story.find("time", {"data-alias": "card_timestamp"})
                if time_element is not None:
                    story_data["time"] = time_element.get_text(strip=True)

                thumbnail_image = ""
                thumbnail_element = story.find(
                    "div", {"data-alias": "image__inner-img"}
                )
                if thumbnail_element is not None:
                    img_element = thumbnail_element.find("img")
                    if img_element is not None:
                        thumbnail_image = img_element.get("src")

                # If no src found, fall back to the img tag
                if not thumbnail_image:
                    image_element = story.find("img")
                    if image_element is not None:
                        thumbnail_image = image_element.get(
                            "data-img-url", image_element.get("src")
                        )

                story_data["thumbnail"] = thumbnail_image
                stories.append(story_data)

        return stories

    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
        json_list = []
        captured_date, captured_time = self.get_current_date_and_time()

        for obj in objects:

            publish_date = ""
            publish_time = ""

            json_list.append(
                {
                    "source": "indiewire",
                    "sourceIconURL": "indiewire",
                    "sourceSection": ", ".join(
                        obj.get("category", [])
                    ),  # or obj.get("category", [""])[0]
                    "title": obj.get("title", ""),
                    "content": (
                        obj.get("content", [])
                        if isinstance(obj.get("content"), list)
                        else []
                    ),  # Ensure content is a list
                    "author": obj.get("author", ""),
                    "urlArticle": obj.get(
                        "url", ""
                    ),  # This should match your story data structure
                    "link": obj.get("link", ""),
                    "urlArticle": obj.get("link", ""),
                    "urlBannerImage": obj.get("banner", ""),
                    "urlThumbnailImage": obj.get("banner", ""),
                    "date": obj.get("time", ""),
                    "categories": obj.get(
                        "category", ""
                    ),  # Ensure this is a string if required\
                    "publishedDate": captured_date,
                    "publishedTime": captured_time,
                    "capturedDate": captured_date,
                    "capturedTime": captured_time,
                }
            )

        return json_list


# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")
