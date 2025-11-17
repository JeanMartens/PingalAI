"""
BBG Wiki Scraper
Extracts structured data from BBG mod wiki for RAG system
Separate extraction methods for each page type
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Any
import re
from urllib.parse import unquote


class BBGWikiScraper:
    def __init__(self, base_url: str = "https://civ6bbg.github.io"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Define all pages and their categories (matches actual URLs)
        self.pages = {
            'leaders': 'leader',
            'bbg_expanded': 'expansion_content',
            'city_states': 'city_state',
            'religion': 'religion',
            'governor': 'governor',
            'great_people': 'great_person',
            'natural_wonder': 'natural_wonder',
            'world_wonder': 'wonder',
            'buildings': 'building',
            'units': 'unit',
            'names': 'naming',
            'policies': 'policy',
            'congress': 'world_congress',
            'misc': 'miscellaneous',
            'changelog': 'changelog',
        }
        
        # All BBG versions (newest to oldest)
        # self.versions = ['7.2', '7.1', '6.5', '6.4', '6.3', '6.2', '6.1', '6.0', '5.8', '5.7', '5.6', 'base_game']
        self.versions = ['7.2', '7.1']
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # ===== PAGE-SPECIFIC EXTRACTION METHODS =====
    
    def extract_leaders(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract leaders - each leader in a div with ID and class='row'"""
        sections = []
        
        # Find all divs with IDs and class='row' (these are leaders)
        leader_divs = soup.find_all('div', class_='row', id=True)
        
        for div in leader_divs:
            leader_id = div.get('id', '')
            
            # Skip non-leader IDs
            if not leader_id or leader_id in ['footer-popup', 'donateText']:
                continue
            
            leader_name = unquote(leader_id)
            content_text = self.clean_text(div.get_text())
            
            if content_text and len(content_text) > 100:
                sections.append({
                    'heading': leader_name,
                    'content': [content_text]
                })
        
        return sections
    
    def extract_city_states(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract city states - they use h2.civ-name, not IDs"""
        sections = []
        
        # Find all chart divs with h2.civ-name
        chart_divs = soup.find_all('div', class_='chart')
        
        for div in chart_divs:
            # Look for h2 with class='civ-name'
            h2 = div.find('h2', class_='civ-name')
            
            if not h2:
                continue
            
            cs_name = self.clean_text(h2.get_text())
            
            if not cs_name:
                continue
            
            # Get the description (p.actual-text)
            desc_elem = div.find('p', class_='actual-text')
            
            if desc_elem:
                description = self.clean_text(desc_elem.get_text())
                
                if description and len(description) > 20:
                    sections.append({
                        'heading': cs_name,
                        'content': [description]
                    })
        
        return sections
    
    def extract_religion(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract religion beliefs with 3-level hierarchy: type -> name -> buff"""
        sections = []
        
        # Find all belief type sections (Pantheon, Follower, etc.)
        belief_type_divs = soup.find_all('div', class_='row', id=True)
        
        for type_div in belief_type_divs:
            belief_type_id = type_div.get('id', '')
            
            # Skip non-belief IDs
            if not belief_type_id or belief_type_id in ['footer-popup', 'donateText']:
                continue
            
            belief_type = unquote(belief_type_id)  # e.g., "Pantheon", "Follower"
            
            # Find all col-lg-* divs within this type
            col_divs = type_div.find_all('div', class_=lambda x: x and 'col-lg-' in x)
            
            for col in col_divs:
                # Find the belief name (h2.civ-name)
                h2 = col.find('h2', class_='civ-name')
                
                if not h2:
                    continue
                
                belief_name = self.clean_text(h2.get_text())
                
                if not belief_name:
                    continue
                
                # Find the description (p.actual-text)
                desc_elem = col.find('p', class_='actual-text')
                
                if desc_elem:
                    description = self.clean_text(desc_elem.get_text())
                    
                    if description and len(description) > 20:
                        sections.append({
                            'heading': f"{belief_type}: {belief_name}",
                            'content': [description]
                        })
        
        return sections
    
    def extract_generic(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Generic extraction for other page types"""
        sections = []
        
        # Find all divs with class='row' and IDs
        item_divs = soup.find_all('div', class_='row', id=True)
        
        for div in item_divs:
            item_id = div.get('id', '')
            
            # Skip common non-content IDs
            if not item_id or item_id in ['footer-popup', 'donateText']:
                continue
            
            item_name = unquote(item_id)
            content_text = self.clean_text(div.get_text())
            
            if content_text and len(content_text) > 50:
                sections.append({
                    'heading': item_name,
                    'content': [content_text]
                })
        
        return sections
    
    # ===== MAIN EXTRACTION METHOD =====
    
    def extract_page_content(self, page_name: str, category: str, version: str) -> Dict[str, Any]:
        """Extract content from a specific BBG page version"""
        url = f"{self.base_url}/en_US/{page_name}_{version}.html"
        
        print(f"    v{version}...", end=" ")
        soup = self.get_page(url)
        
        if not soup:
            print("✗")
            return None
        
        version_display = "Base Game" if version == "base_game" else f"v{version}"
        title = f"BBG {page_name.replace('_', ' ').title()} {version_display}"
        
        # Route to appropriate extraction method based on page name
        if page_name == 'leaders':
            sections = self.extract_leaders(soup)
        elif page_name == 'city_states':
            sections = self.extract_city_states(soup)
        elif page_name == 'religion':
            sections = self.extract_religion(soup)
        else:
            sections = self.extract_generic(soup)
        
        if not sections:
            print("✗")
            return None
        
        print(f"✓ ({len(sections)})")
        
        return {
            'title': title,
            'url': url,
            'category': category,
            'page_name': page_name,
            'bbg_version': version,
            'sections': sections,
            'metadata': {
                'mod': 'bbg',
                'version': version
            },
            'source': 'bbg_wiki'
        }
    
    def scrape_all_versions(self, page_name: str, category: str) -> List[Dict[str, Any]]:
        """Scrape a page across all BBG versions"""
        results = []
        
        for version in self.versions:
            data = self.extract_page_content(page_name, category, version)
            if data:
                results.append(data)
            time.sleep(0.3)
        
        return results
    
    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all BBG pages across all versions"""
        all_data = {}
        
        print("\n" + "="*60)
        print("BBG WIKI SCRAPER - ALL VERSIONS")
        print("="*60)
        print(f"Versions: {len(self.versions)}")
        print(f"Pages: {len(self.pages)}")
        print("="*60)
        
        for page_name, category in self.pages.items():
            print(f"\n[{page_name.upper()}]")
            
            page_data = self.scrape_all_versions(page_name, category)
            
            if page_data:
                if category not in all_data:
                    all_data[category] = []
                all_data[category].extend(page_data)
                print(f"  ✓ {len(page_data)} versions")
            else:
                print(f"  ✗ Failed")
        
        return all_data
    
    def save_to_json(self, data: Dict, filename: str):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved: {filename}")


def main():
    scraper = BBGWikiScraper()
    all_data = scraper.scrape_all()
    scraper.save_to_json(all_data, "data/raw/bbg_wiki/bbg_complete_data.json")
    
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    total = sum(len(pages) for pages in all_data.values())
    print(f"Total documents: {total}")
    for category, pages in sorted(all_data.items()):
        print(f"  {category}: {len(pages)}")


if __name__ == "__main__":
    main()