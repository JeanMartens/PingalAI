"""
Civilization VI Wiki Scraper
Extracts structured data from the Civ6 Fandom wiki for RAG system
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Any
from urllib.parse import urljoin
import re


class Civ6WikiScraper:
    def __init__(self, base_url: str = "https://civilization.fandom.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove reference brackets like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)
        return text.strip()
    
    def extract_civilizations(self) -> List[Dict[str, Any]]:
        """Extract all civilizations from the main Civ6 page"""
        main_url = f"{self.base_url}/wiki/Civilization_VI"
        soup = self.get_page(main_url)
        
        if not soup:
            return []
        
        civilizations = []
        
        # Find the civilizations table
        # The table has class "wikitable" and contains civilization data
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                
                if len(cells) < 3:  # Skip incomplete rows
                    continue
                
                # Extract civilization name and link
                civ_link = cells[0].find('a')
                if not civ_link:
                    continue
                
                civ_name = self.clean_text(civ_link.get_text())
                civ_url = urljoin(self.base_url, civ_link['href'])
                
                # Extract leader information
                leaders = []
                leader_cells = cells[1].find_all('a')
                for leader_link in leader_cells:
                    leader_name = self.clean_text(leader_link.get_text())
                    leader_url = urljoin(self.base_url, leader_link['href'])
                    leaders.append({
                        'name': leader_name,
                        'url': leader_url
                    })
                
                civilizations.append({
                    'name': civ_name,
                    'url': civ_url,
                    'leaders': leaders,
                    'category': 'civilization'
                })
        
        return civilizations
    
    def extract_page_content(self, url: str, category: str) -> Dict[str, Any]:
        """Extract detailed content from a specific page"""
        soup = self.get_page(url)
        
        if not soup:
            return None
        
        # Get the page title
        title_elem = soup.find('h1', class_='page-header__title')
        title = self.clean_text(title_elem.get_text()) if title_elem else ""
        
        # Extract main content
        content_div = soup.find('div', class_='mw-parser-output')
        
        if not content_div:
            return None
        
        # Extract all paragraphs and sections
        sections = []
        current_section = {
            'heading': 'Introduction',
            'content': []
        }
        
        for element in content_div.children:
            if element.name in ['h2', 'h3', 'h4']:
                # Save previous section if it has content
                if current_section['content']:
                    sections.append(current_section)
                
                # Start new section
                heading_text = self.clean_text(element.get_text())
                # Remove [edit] links
                heading_text = heading_text.replace('[edit]', '').strip()
                
                current_section = {
                    'heading': heading_text,
                    'content': []
                }
            
            elif element.name == 'p':
                # Extract paragraph text
                text = self.clean_text(element.get_text())
                if text and len(text) > 50:  # Only keep substantial paragraphs
                    current_section['content'].append(text)
            
            elif element.name == 'ul' or element.name == 'ol':
                # Extract list items
                list_items = element.find_all('li')
                for item in list_items:
                    text = self.clean_text(item.get_text())
                    if text and len(text) > 30:
                        current_section['content'].append(text)
        
        # Add the last section
        if current_section['content']:
            sections.append(current_section)
        
        # Extract infobox data (stats, abilities, etc.)
        infobox = soup.find('aside', class_='portable-infobox')
        metadata = {}
        
        if infobox:
            # Extract key-value pairs from infobox
            data_items = infobox.find_all('div', class_='pi-item')
            for item in data_items:
                label_elem = item.find('h3', class_='pi-data-label')
                value_elem = item.find('div', class_='pi-data-value')
                
                if label_elem and value_elem:
                    label = self.clean_text(label_elem.get_text())
                    value = self.clean_text(value_elem.get_text())
                    metadata[label] = value
        
        return {
            'title': title,
            'url': url,
            'category': category,
            'sections': sections,
            'metadata': metadata,
            'source': 'civ6_wiki'
        }
    
    def get_category_pages(self, category_url: str) -> List[str]:
        """Get all page URLs from a category page"""
        soup = self.get_page(category_url)
        
        if not soup:
            return []
        
        page_urls = []
        
        # Find all links in the category
        category_content = soup.find('div', class_='category-page__members')
        if category_content:
            links = category_content.find_all('a', class_='category-page__member-link')
            for link in links:
                page_urls.append(urljoin(self.base_url, link['href']))
        
        return page_urls
    
    def scrape_category(self, category_name: str, category_url: str) -> List[Dict[str, Any]]:
        """Scrape all pages in a category"""
        print(f"\nScraping category: {category_name}")
        
        page_urls = self.get_category_pages(category_url)
        results = []
        
        for i, url in enumerate(page_urls, 1):
            print(f"  Processing {i}/{len(page_urls)}: {url}")
            
            data = self.extract_page_content(url, category_name)
            if data:
                results.append(data)
            
            # Be nice to the server
            time.sleep(1)
        
        return results
    
    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Main scraping function - scrape all important categories"""
        
        all_data = {}
        
        # Define categories to scrape
        categories = {
            'civilizations': f"{self.base_url}/wiki/Category:Civilizations_(Civ6)",
            'leaders': f"{self.base_url}/wiki/Category:Leaders_(Civ6)",
            'units': f"{self.base_url}/wiki/Category:Units_(Civ6)",
            'buildings': f"{self.base_url}/wiki/Category:Buildings_(Civ6)",
            'wonders': f"{self.base_url}/wiki/Category:Wonders_(Civ6)",
            'districts': f"{self.base_url}/wiki/Category:Districts_(Civ6)",
            'improvements': f"{self.base_url}/wiki/Category:Tile_improvements_(Civ6)",
            'game_concepts': f"{self.base_url}/wiki/Category:Game_concepts_(Civ6)",
        }
        
        for category_name, category_url in categories.items():
            all_data[category_name] = self.scrape_category(category_name, category_url)
        
        return all_data
    
    def save_to_json(self, data: Dict, filename: str = "civ6_wiki_data.json"):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to {filename}")


def main():
    """Example usage"""
    scraper = Civ6WikiScraper()
    
    # Option 1: Scrape everything (takes a while!)
    # all_data = scraper.scrape_all()
    # scraper.save_to_json(all_data, "civ6_complete_data.json")
    
    # Option 2: Scrape specific category
    print("Scraping civilizations...")
    civs = scraper.scrape_category(
        'civilizations',
        'https://civilization.fandom.com/wiki/Category:Civilizations_(Civ6)'
    )
    scraper.save_to_json({'civilizations': civs}, "civ6_civilizations.json")
    
    # Option 3: Scrape a specific page
    print("\nScraping Greece page as example...")
    greece_data = scraper.extract_page_content(
        'https://civilization.fandom.com/wiki/Greek_(Civ6)',
        'civilization'
    )
    
    if greece_data:
        print(f"\nExtracted data for: {greece_data['title']}")
        print(f"Number of sections: {len(greece_data['sections'])}")
        print(f"\nSection headings:")
        for section in greece_data['sections']:
            print(f"  - {section['heading']}")
        
        print(f"\nMetadata:")
        for key, value in greece_data['metadata'].items():
            print(f"  {key}: {value}")
        
        # Save example
        scraper.save_to_json(greece_data, "greece_example.json")


if __name__ == "__main__":
    main()