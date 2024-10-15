from datetime import datetime
from typing import List, Dict, Union, Optional
from .abstract import AbstractSource
from loguru import logger
import sys
import requests
from bs4 import BeautifulSoup


class NyTimes(AbstractSource):
    def __init__(self):
        self.domain = "https://www.nytimes.com"

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html_data = BeautifulSoup(response.content, "html.parser")
            return html_data
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
        logger.info("Getting stories from the page")
        stories = []

        parent_div = soup.find("div", class_="css-13mho3u")
        if parent_div:
            list_items = parent_div.find_all("li", class_="css-18yolpw")
            for item in list_items:
                title_element = item.find("h3", class_="css-1j88qqx e15t083i0")
                title = title_element.get_text(strip=True) if title_element else None

                description_element = item.find("p", class_="css-1pga48a e15t083i1")
                description = (
                    description_element.get_text(strip=True)
                    if description_element
                    else None
                )

                author_element = item.find("p", class_="css-1y3ykdt e140qd2t0")
                author = (
                    author_element.get_text(strip=True).replace("By ", "")
                    if author_element
                    else None
                )

                date = item.select_one("div > div > span").get_text(strip=True)

                banner_image = item.select_one("figure").find('div').find('img')
                if banner_image:
                    banner = banner_image.get("src")

                link_element = item.find("a", class_="css-8hzhxf")
                article_url = (
                    self.domain + link_element.get("href") if link_element else None
                )

                stories.append(
                    {
                        "title": title,
                        "content": description,
                        "categories": [],
                        "author": author,
                        "date": date,
                        "link": article_url,
                        "banner": banner,
                    }
                )

        return stories

    def to_json(
        self, objects: List[Dict[str, Optional[str]]]
    ) -> List[Dict[str, Union[str, List[str]]]]:
        json_list = []
        captured_date = datetime.now().strftime("%Y-%m-%d")
        captured_time = datetime.now().strftime("%H:%M:%S")

        for obj in objects:
            date = obj.get("date")
            publish_date = ""
            publish_time = ""

            if obj.get("time"):
                publish_date, publish_time = self.extract_date_time_from_iso(
                    obj["time"]
                )
            if date:
                try:
                    parsed_date = datetime.strptime(date, "%b. %d, %Y")
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Couldn't parse date: {date}")
                    formatted_date = date  # Keep the original string if parsing fails
            else:
                formatted_date = None

            # json_list.append({
            #     "source": 'nytimes',
            #     "sourceIconURL": 'nytimes',
            #     "sourceSection": 'Movies',  # Adjust if you have specific sections
            #     "title": obj.get("title", ""),
            #     "content": [obj.get("content", "")],  # Wrap content in a list
            #     "categories": obj.get("categories", []),
            #     "author": obj.get("author", ""),
            #     "date": formatted_date,
            #     "link": obj.get("link", ""),
            #     "capturedDate": captured_date,
            #     "capturedTime": captured_time
            # })

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
                    "urlThumbnailImage": obj.get("banner", ""),
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
