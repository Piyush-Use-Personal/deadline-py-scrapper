import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve the page: {response.status_code}")
        return None

def extract_data(soup):
    data = []
    entries = soup.find_all('a', class_='c-title__link')
    for entry in entries:
        # Extract relevant fields, e.g., text content
        text = entry.get_text(strip=True)
        data.append(text)
    return data
