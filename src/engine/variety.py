import sys
from loguru import logger
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Union

from .abstract import AbstractSource

# Configure loguru to output logs to the console
logger.remove()
logger.add(sys.stdout, level="INFO")

class Variety(AbstractSource):

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
        list_items = soup.find_all('li', class_='o-tease-list__item')

        for item in list_items:
            title_element = item.find('h3', class_='c-title')
            title = title_element.get_text(strip=True) if title_element else None
            
            thumbnail_element = item.find('img', class_='c-lazy-image__img')
            thumbnail = thumbnail_element['src'] if thumbnail_element else None
            
            category_element = item.find('a', class_='c-span__link')
            category = category_element.get_text(strip=True) if category_element else None
            
            article_url_element = item.find('a', class_='c-title__link')
            article_url = article_url_element['href'] if article_url_element else None

            if title and thumbnail and category and article_url:
                stories.append({
                    'title': title,
                    'thumbnail': thumbnail,
                    'category': category,
                    'url': article_url
                })

        return stories

    def get_child_links(self, firstPageSoup: BeautifulSoup) -> List[str]:
        """
        Extracts parent links from the given BeautifulSoup object.
        Returns a list of URLs.
        """
        logger.info("Getting parent links")
        parent_links = []
        links = firstPageSoup.find_all('a', class_="c-title__link")
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
            try:
                if content:
                    title = self.get_headline(content)
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
                        "author_url": author_link
                    }
                    processed_contents.append(processed_content)
            except Exception as e:
                return None
        return processed_contents

    def get_headline(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the headline (title) from the given BeautifulSoup object.
        Returns the title as a string or None if not found.
        """
        logger.info("Getting title")
        title_element = soup.find('h1', id='section-heading')
        if title_element:
            return title_element.get_text(strip=True)
        return None

    def get_banner_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the banner image URL from the given BeautifulSoup object.
        Returns the URL as a string or None if not found.
        """
        logger.info("Getting banner image")
        banner_element = soup.find('img', class_='c-lazy-image__img')
        banner_url = banner_element['src'] if banner_element else None
        return banner_url

    def get_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts the main content from the given BeautifulSoup object.
        Returns a list of text content.
        """
        logger.info("Getting child content")
        child_contents = []
        for p in soup.find_all('p', class_='paragraph'):
            child_contents.append(p.get_text(strip=True))
        return child_contents

    def get_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the author name(s) from the given BeautifulSoup object.
        Returns the author's name(s) as a comma-separated string or None if not found.
        """
        logger.info("Getting author")
        
        # Try to get authors from the 'lrv-u-margin-tb-00' class
        author_element = soup.find('p', class_='lrv-u-margin-tb-00')
        if author_element:
            author_link = author_element.find('a', class_='c-link')
            if author_link:
                return author_link.get_text(strip=True)
        
        # Try to get authors from the 'c-tagline' class (multiple authors)
        author_elements = soup.find('div', class_='c-tagline')
        if author_elements:
            authors = author_elements.find_all('a', class_='c-link')
            if authors:
                author_names = [author.get_text(strip=True) for author in authors]
                return ', '.join(author_names)
        
        return None

        
    def get_author_link(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """
        Retrieves the author link URLs from the given BeautifulSoup object.
        Returns a list of URLs as strings or None if not found.
        """
        logger.info("Getting author links")

        # Try to find author links within the 'c-tagline' class
        author_links = [
            a['href'] for a in soup.select('div.c-tagline a.c-link')
        ]

        # If no links are found in 'c-tagline', try the 'lrv-u-margin-tb-00' class
        if not author_links:
            author_paragraph = soup.find('p', class_='lrv-u-margin-tb-00')
            if author_paragraph:
                author_element = author_paragraph.find('a', class_='c-link')
                if author_element:
                    author_links.append(author_element['href'])

        return author_links if author_links else None

    
    def get_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Retrieves the publication date from the given BeautifulSoup object.
        Returns the date as a string or None if not found.
        """
        logger.info("Getting date")
        date_element = soup.find('time', class_='c-timestamp')
        if date_element:
            return date_element.get_text(strip=True)
        return None

    def get_categories(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts categories from the given BeautifulSoup object.
        Returns a list of category names.
        """
        logger.info("Getting categories")
        breadcrumb_list = soup.find('ol', class_='o-nav-breadcrumblist__list')
        categories = [li.get_text(strip=True) for li in breadcrumb_list.find_all('a')]
        
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
                "source": 'variety',
                "sourceIconURL": 'variety',
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
