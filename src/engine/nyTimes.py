import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Dict, Optional, Union
from datetime import datetime

from .abstract import AbstractSource

# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")

class NyTimes(AbstractSource):
    def __init__(self):
        self.domain = "https://www.nytimes.com"

    def process(self, url: str) -> List[Dict[str, Union[str, List[str]]]]:
        stories = []
        firstPageSoup = self.get_primary_content(url)
        if firstPageSoup:
            stories = self.get_stories(firstPageSoup)
        return self.to_json(stories)

    def process_children(self, soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
        """
        Processes any child elements if needed.
        Currently serves as a placeholder for future enhancements.
        """
        logger.info("Processing child elements")
        # Implement child processing logic here if necessary
        return []

    def get_primary_content(self, url: str) -> Optional[BeautifulSoup]:
        logger.info(f"Fetching primary content from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            logger.error(f"Failed to retrieve the page: {response.status_code}")
            return None

    def get_stories(self, soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
                logger.info("Getting stories from the page")
                stories = []
                
                parent_div = soup.find('div', class_='css-13mho3u')
                if parent_div:
                    list_items = parent_div.find_all('li', class_='css-18yolpw')
                    for item in list_items:
                        title_element = item.find('h3', class_='css-1j88qqx e15t083i0')
                        title = title_element.get_text(strip=True) if title_element else None

                        description_element = item.find('p', class_='css-1pga48a e15t083i1')
                        description = description_element.get_text(strip=True) if description_element else None

                        author_element = item.find('p', class_='css-1y3ykdt e140qd2t0')
                        author = author_element.get_text(strip=True).replace('By ', '') if author_element else None

                        date_element = item.find('span', attrs={'data-testid': 'todays-date'})
                        date = date_element.get_text(strip=True) if date_element else None

                        link_element = item.find('a', class_='css-8hzhxf')
                        url = self.domain + link_element.get('href') if link_element else None

                        stories.append({
                            'title': title,
                            'content': description,
                            'categories': [],
                            'author': author,
                            'date': date,
                            'link': url
                        })
                
                return stories





    def to_json(self, objects: List[Dict[str, Optional[str]]]) -> List[Dict[str, Union[str, List[str]]]]:
        json_list = []
        captured_date = datetime.now().strftime('%Y-%m-%d')
        captured_time = datetime.now().strftime('%H:%M:%S')
        
        for obj in objects:
            json_list.append({
                "source": 'nytimes',
                "sourceIconURL": 'nytimes',
                "sourceSection": 'Movies',  # Adjust if you have specific sections
                "title": obj.get("title", ""),
                "content": [obj.get("content", "")],  # Wrap content in a list
                "categories": obj.get("categories", []),  # Assuming categories can be a list
                "author": obj.get("author", ""),
                "date": obj.get("date", ""),
                "link": obj.get("link", ""),
                "capturedDate": captured_date,
                "capturedTime": captured_time
            })
        
        return json_list

