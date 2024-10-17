from datetime import datetime
from typing import List, Dict, Union, Optional
from .abstract import AbstractSource
from loguru import logger
import sys
import requests
from bs4 import BeautifulSoup


class LATimes(AbstractSource):
    def __init__(self):
        self.domain = "https://www.latimes.com/"
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
                banner = self.get_banner_image(content)
                category = self.get_category(content)
                author = self.get_author(content)
                date_and_time = self.get_date_and_time(content)

                processed_content = {
                    # "title": title,
                    "content": child_content,
                    "author": author,
                    "category": [category],
                    "link": url,
                    "banner": banner,
                    "publishedTime": date_and_time.get("publishedTime"),
                    "publishedDate": date_and_time.get("publishedDate"),
                }
                processed_contents.append(processed_content)

        # Return after all URLs are processed
        return processed_contents


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
        heading_image = soup.find("img", class_="image")
        if heading_image:
            return heading_image.get("srcset")
        return None

    def get_author(self, soup: BeautifulSoup) -> Optional[str]:
        logger.info("Getting author")
        try:
            author_element = soup.find("div", class_="author-name")
            if author_element:
                return author_element.find("a").get_text(strip=True)
            return None
        except AttributeError as e:
            logger.error(f"Failed to extract author: {e}")
            return None

    def get_date_and_time(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        logger.info("Getting date and time")
        try:
            # Attempt to find the time tag
            time_tag = soup.find("time", class_="published-date")

            # Check if time_tag is found
            if time_tag is None:
                logger.warning("Published date element not found.")
                return None

            # Find the published date and time elements
            published_date_element = time_tag.find("span", class_="published-date-day")
            published_time_element = time_tag.find("span", class_="published-time")

            # Check if both elements are found
            if published_date_element is None:
                logger.warning("Published date element not found.")
            if published_time_element is None:
                logger.warning("Published time element not found.")

            # If both elements are found, extract their text
            published_date = published_date_element.get_text(strip=True) if published_date_element else None
            published_time = published_time_element.get_text(strip=True) if published_time_element else None

            # Return a dictionary with the date and time, ensuring both are not None
            return {
                "publishedDate": published_date,
                "publishedTime": published_time
            }

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
        elements = soup.find("div", {"data-element": "story-body"})
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

        parent_UL = soup.find("ul", class_="list-menu list-i-menu")

        if parent_UL:
            for story in parent_UL.find_all("li"):
                story_data = {}

                # outer_div = story.find("div", {"data-alias": "card__main"})
                # if outer_div is not None:
                #     category_div = outer_div.find("div", {"data-alias": "card__kicker"})
                #     if category_div is not None:
                #         category = category_div.get_text(strip=True)
                #         story_data["category"] = [category]

                title_h2 = story.find("h2", class_="promo-title")
                if title_h2 is not None:
                    title = title_h2.find("a").get_text(strip=True)
                    if title:  # Check if title is not empty
                        story_data["title"] = title

                link_a = story.find("a", class_="link promo-placeholder")
                if link_a:
                    story_data["link"] = link_a.get("href")

                # author_div = story.find("div", {"data-alias": "byline__text-wrapper"})
                # if author_div is not None:
                #     author_span = author_div.find("span")
                #     if author_span is not None:
                #         story_data["author"] = author_span.get_text(strip=True)

                # time_element = story.find("time", {"data-alias": "card_timestamp"})
                # if time_element is not None:
                #     story_data["time"] = time_element.get_text(strip=True)

                # thumbnail_image = ""
                # thumbnail_element = story.find(
                #     "div", {"data-alias": "image__inner-img"}
                # )
                # if thumbnail_element is not None:
                #     img_element = thumbnail_element.find("img")
                #     if img_element is not None:
                #         thumbnail_image = img_element.get("src")

                # # If no src found, fall back to the img tag
                # if not thumbnail_image:
                #     image_element = story.find("img")
                #     if image_element is not None:
                #         thumbnail_image = image_element.get(
                #             "data-img-url", image_element.get("src")
                #         )

                # story_data["thumbnail"] = thumbnail_image
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
                    "source": "latimes",
                    "sourceIconURL": "latimes",
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
                        "link", ""
                    ),  # This should match your story data structure
                    "link": obj.get("link", ""),
                    "urlArticle": obj.get("link", ""),
                    "urlBannerImage": obj.get("banner", ""),
                    "urlThumbnailImage": obj.get("banner", ""),
                    "date": obj.get("publishedDate", ""),
                    "categories": obj.get(
                        "category", ""
                    ),  # Ensure this is a string if required\
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
