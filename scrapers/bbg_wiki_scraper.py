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
        
        self.versions = ['7.2']
    
    def get_page(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            return None
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_leaders(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        sections = []
        leader_divs = soup.find_all('div', class_='row', id=True)
        
        for div in leader_divs:
            leader_id = div.get('id', '')
            
            if not leader_id or leader_id in ['footer-popup', 'donateText']:
                continue
            
            leader_name = unquote(leader_id)
            
            # Find the chart div
            chart = div.find('div', class_='chart')
            if not chart:
                continue
            
            # Extract only the main descriptions (p.actual-text), skip base-game-text comparison divs
            main_descs = chart.find_all('p', class_='actual-text')
            
            content_parts = []
            for desc in main_descs:
                text = self.clean_text(desc.get_text())
                if text:
                    content_parts.append(text)
            
            if content_parts:
                sections.append({
                    'heading': leader_name,
                    'content': content_parts
                })
        
        return sections
    
    def extract_city_states(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        sections = []
        chart_divs = soup.find_all('div', class_='chart')
        
        for div in chart_divs:
            h2 = div.find('h2', class_='civ-name')
            
            if not h2:
                continue
            
            cs_name = self.clean_text(h2.get_text())
            
            if not cs_name:
                continue
            
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
        sections = []
        belief_type_divs = soup.find_all('div', class_='row', id=True)
        
        for type_div in belief_type_divs:
            belief_type_id = type_div.get('id', '')
            
            if not belief_type_id or belief_type_id in ['footer-popup', 'donateText']:
                continue
            
            belief_type = unquote(belief_type_id)
            col_divs = type_div.find_all('div', class_=lambda x: x and 'col-lg-' in x)
            
            for col in col_divs:
                h2 = col.find('h2', class_='civ-name')
                
                if not h2:
                    continue
                
                belief_name = self.clean_text(h2.get_text())
                
                if not belief_name:
                    continue
                
                desc_elem = col.find('p', class_='actual-text')
                
                if desc_elem:
                    description = self.clean_text(desc_elem.get_text())
                    
                    if description and len(description) > 20:
                        sections.append({
                            'heading': f"{belief_type}: {belief_name}",
                            'content': [description]
                        })
        
        return sections
    
    def extract_governors(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        sections = []
        chart_divs = soup.find_all('div', class_='chart')
        
        for div in chart_divs:
            h2 = div.find('h2', class_='civ-name')
            
            if not h2:
                continue
            
            governor_name = self.clean_text(h2.get_text())
            
            if not governor_name:
                continue
            
            promotions = div.find_all('h3', class_='civ-ability-name')
            
            for h3 in promotions:
                promotion_text = ""
                for child in h3.children:
                    if child.name == 'br':
                        break
                    if child.name == 'p':
                        break
                    if isinstance(child, str):
                        promotion_text += child
                
                promotion_name = self.clean_text(promotion_text)
                desc_elem = h3.find('p', class_='civ-ability-desc')
                
                if desc_elem:
                    description = self.clean_text(desc_elem.get_text())
                    
                    if promotion_name and description:
                        sections.append({
                            'heading': f"{governor_name}: {promotion_name}",
                            'content': [description]
                        })
        
        return sections
    
    def extract_great_people(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract great people: Type -> Era -> Name -> (Charges + Description)"""
        sections = []
        
        current_type = None
        current_era = None
        
        # Find all row divs in order
        all_rows = soup.find_all('div', class_='row')
        
        for row in all_rows:
            row_id = row.get('id', '')
            
            # Skip non-great-people IDs
            if row_id and row_id in ['footer-popup', 'donateText']:
                continue
            
            # Check if this is a type header (has ID and h2.civ-name)
            if row_id:
                h2 = row.find('h2', class_='civ-name')
                if h2:
                    current_type = self.clean_text(h2.get_text())
                    current_era = None
                    continue
            
            # Check if this is an era header (has ID and h3.civ-name)
            if row_id:
                h3 = row.find('h3', class_='civ-name')
                if h3:
                    current_era = self.clean_text(h3.get_text())
                    continue
            
            # This must be a person row (no ID, has chart divs)
            if not row_id and current_type and current_era:
                charts = row.find_all('div', class_='chart')
                
                for chart in charts:
                    # Find name (first p.civ-ability-name)
                    name_elems = chart.find_all('p', class_='civ-ability-name')
                    
                    if not name_elems:
                        continue
                    
                    gp_name = self.clean_text(name_elems[0].get_text())
                    
                    if not gp_name:
                        continue
                    
                    # Check if second p.civ-ability-name has charges
                    charges = "1"
                    if len(name_elems) > 1:
                        charges_text = self.clean_text(name_elems[1].get_text())
                        if charges_text.isdigit():
                            charges = charges_text
                    
                    # Find description (p.civ-ability-desc)
                    desc_elem = chart.find('p', class_='civ-ability-desc')
                    
                    if desc_elem:
                        description = self.clean_text(desc_elem.get_text())
                        
                        if description:
                            sections.append({
                                'heading': f"{current_type} - {current_era}: {gp_name}",
                                'content': [f"Charges: {charges}", description]
                            })
        
        return sections
    
    def extract_natural_wonders(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract natural wonders - each has its own row with ID"""
        sections = []
        
        # Find all row divs with IDs (each natural wonder)
        all_rows = soup.find_all('div', class_='row', id=True)
        
        for row in all_rows:
            wonder_id = row.get('id', '')
            
            # Skip non-wonder IDs
            if not wonder_id or wonder_id in ['footer-popup', 'donateText']:
                continue
            
            # Find the chart div inside
            chart = row.find('div', class_='chart')
            
            if not chart:
                continue
            
            # Find name (h2.civ-name) - for verification
            name_h2 = chart.find('h2', class_='civ-name')
            
            if not name_h2:
                continue
            
            wonder_name = self.clean_text(name_h2.get_text())
            
            if not wonder_name:
                continue
            
            # Find description (p.actual-text - primary description for natural wonders)
            desc_elem = chart.find('p', class_='actual-text')
            
            if desc_elem:
                description = self.clean_text(desc_elem.get_text())
                
                if description and len(description) > 20:
                    sections.append({
                        'heading': wonder_name,
                        'content': [description]
                    })
        
        return sections
    
    def extract_misc(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract misc page: Dark Age Policies and Golden Age Dedications by era"""
        sections = []
        
        current_era = None
        
        # Find all row divs in order
        all_rows = soup.find_all('div', class_='row')
        
        for row in all_rows:
            row_id = row.get('id', '')
            
            # Skip common non-content IDs
            if row_id and row_id in ['footer-popup', 'donateText']:
                continue
            
            # Check if this is an era header
            if row_id:
                h2 = row.find('h2', class_='civ-name')
                if h2:
                    era_name = self.clean_text(h2.get_text())
                    if 'Era' in era_name:
                        current_era = era_name
                        continue
            
            if not current_era:
                continue
            
            # Check if this row has a single chart with nested row (Golden Age Dedications)
            charts = row.find_all('div', class_='chart', recursive=False)
            
            if len(charts) == 1:
                # This might be Golden Age Dedications
                nested_row = charts[0].find('div', class_='row')
                if nested_row:
                    # Find all dedication columns
                    cols = nested_row.find_all('div', class_=lambda x: x and 'col-lg-' in x)
                    for col in cols:
                        desc_elem = col.find('p', class_='civ-ability-desc')
                        if desc_elem:
                            desc_text = self.clean_text(desc_elem.get_text())
                            if desc_text and 'Golden Age' in desc_text:
                                # Extract dedication name (everything before "Golden Age:")
                                if 'Golden Age:' in desc_text:
                                    dedication_name = desc_text.split('Golden Age:')[0].strip()
                                    sections.append({
                                        'heading': f"Golden Age Dedication - {current_era}: {dedication_name}",
                                        'content': [desc_text]
                                    })
            else:
                # Multiple charts - likely Dark Age Policies
                for chart in charts:
                    name_h2 = chart.find('h2', class_='civ-name')
                    if not name_h2:
                        continue
                    
                    policy_name = self.clean_text(name_h2.get_text())
                    if not policy_name:
                        continue
                    
                    desc_elem = chart.find('p', class_='civ-ability-desc')
                    if desc_elem:
                        desc_text = self.clean_text(desc_elem.get_text())
                        if desc_text and len(desc_text) > 10:
                            sections.append({
                                'heading': f"Dark Age Policy - {current_era}: {policy_name}",
                                'content': [desc_text]
                            })
        
        return sections
    
    def extract_changelog(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract changelog: Category -> Subcategory -> Changes"""
        sections = []
        
        current_category = None
        
        # Find the main chart div
        main_chart = soup.find('div', class_='chart')
        
        if not main_chart:
            return sections
        
        # Find all h1 and h2 headers and p descriptions in order
        for element in main_chart.children:
            if element.name == 'h1' and 'civ-name' in element.get('class', []):
                # Main category (e.g., "Game Mechanics")
                current_category = self.clean_text(element.get_text())
            
            elif element.name == 'h2' and 'civ-name' in element.get('class', []):
                # Subcategory (e.g., "Global Changes", "Combat")
                if current_category:
                    subcategory = self.clean_text(element.get_text())
                    
                    # Look for the next p element
                    next_p = element.find_next_sibling('p', class_='civ-ability-desc')
                    if next_p:
                        description = self.clean_text(next_p.get_text())
                        if description and len(description) > 20:
                            sections.append({
                                'heading': f"{current_category}: {subcategory}",
                                'content': [description]
                            })
        
        return sections
    
    def extract_generic(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Generic extraction for other page types"""
        sections = []
        
        current_category = None
        
        # Find all row divs in order
        all_rows = soup.find_all('div', class_='row')
        
        for row in all_rows:
            row_id = row.get('id', '')
            
            # Skip common non-content IDs
            if row_id and row_id in ['footer-popup', 'donateText']:
                continue
            
            # Check if this is a category/era header (has ID and h2 or h3)
            if row_id:
                h2 = row.find('h2', class_='civ-name')
                h3 = row.find('h3', class_='civ-name')
                if h2:
                    current_category = self.clean_text(h2.get_text())
                    continue
                elif h3:
                    current_category = self.clean_text(h3.get_text())
                    continue
            
            # This is a content row (no ID or ID but has charts)
            charts = row.find_all('div', class_='chart')
            
            for chart in charts:
                # Find name (h2.civ-name)
                name_h2 = chart.find('h2', class_='civ-name')
                
                if not name_h2:
                    continue
                
                item_name = self.clean_text(name_h2.get_text())
                
                if not item_name:
                    continue
                
                # Find all descriptions (p.civ-ability-desc)
                desc_elems = chart.find_all('p', class_='civ-ability-desc')
                
                descriptions = []
                for desc in desc_elems:
                    desc_text = self.clean_text(desc.get_text())
                    if desc_text and len(desc_text) > 10:
                        descriptions.append(desc_text)
                
                if descriptions:
                    heading = f"{current_category}: {item_name}" if current_category else item_name
                    sections.append({
                        'heading': heading,
                        'content': descriptions
                    })
        
        return sections
    
    def extract_page_content(self, page_name: str, category: str, version: str) -> Dict[str, Any]:
        url = f"{self.base_url}/en_US/{page_name}_{version}.html"
        
        print(f"    v{version}...", end=" ")
        soup = self.get_page(url)
        
        if not soup:
            print("✗")
            return None
        
        version_display = "Base Game" if version == "base_game" else f"v{version}"
        title = f"BBG {page_name.replace('_', ' ').title()} {version_display}"
        
        if page_name == 'leaders':
            sections = self.extract_leaders(soup)
        elif page_name == 'city_states':
            sections = self.extract_city_states(soup)
        elif page_name == 'religion':
            sections = self.extract_religion(soup)
        elif page_name == 'governor':
            sections = self.extract_governors(soup)
        elif page_name == 'great_people':
            sections = self.extract_great_people(soup)
        elif page_name == 'natural_wonder':
            sections = self.extract_natural_wonders(soup)
        elif page_name == 'misc':
            sections = self.extract_misc(soup)
        elif page_name == 'changelog':
            sections = self.extract_changelog(soup)
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
        results = []
        
        for version in self.versions:
            data = self.extract_page_content(page_name, category, version)
            if data:
                results.append(data)
            time.sleep(0.3)
        
        return results
    
    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
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
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved: {filename}")


def main():
    scraper = BBGWikiScraper()
    all_data = scraper.scrape_all()
    scraper.save_to_json(all_data, "data/raw/bbg_wiki/bbg_complete_data_v2.json")
    
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    total = sum(len(pages) for pages in all_data.values())
    print(f"Total documents: {total}")
    for category, pages in sorted(all_data.items()):
        print(f"  {category}: {len(pages)}")


if __name__ == "__main__":
    main()