"""
BBG Wiki Scraper
TODO: Implement scraper for Better Balanced Game wiki
"""

from scrapers.civ6_wiki_scraper import Civ6WikiScraper


class BBGWikiScraper(Civ6WikiScraper):
    """Scraper for BBG wiki - to be implemented"""
    
    def __init__(self):
        # Update with actual BBG wiki URL
        super().__init__(base_url="https://bbg.civfanatics.com")
    
    # TODO: Implement BBG-specific scraping methods
