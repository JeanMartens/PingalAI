"""
Complete Example Workflow
Demonstrates the full data collection and processing pipeline
"""

from civ6_wiki_scraper import Civ6WikiScraper
from civ6_rag_processor import Civ6RAGProcessor
import json
import time


def example_1_single_page():
    """Example 1: Scrape and process a single civilization"""
    print("="*60)
    print("EXAMPLE 1: Single Page (Greece)")
    print("="*60)
    
    scraper = Civ6WikiScraper()
    
    # Scrape Greece page
    print("\n1. Scraping Greece page...")
    greece = scraper.extract_page_content(
        'https://civilization.fandom.com/wiki/Greek_(Civ6)',
        'civilization'
    )
    
    if greece:
        print(f"✓ Successfully scraped: {greece['title']}")
        print(f"  - Sections: {len(greece['sections'])}")
        print(f"  - Metadata fields: {len(greece['metadata'])}")
        
        # Process for RAG
        print("\n2. Processing for RAG...")
        processor = Civ6RAGProcessor(chunk_size=600, chunk_overlap=100)
        documents = processor.process_page_data(greece)
        
        print(f"✓ Generated {len(documents)} document chunks")
        
        # Save
        processor.save_processed_data(documents, 'example_greece_rag.json')
        
        # Show example document
        print("\n3. Example document:")
        if documents:
            doc = documents[0]
            print(f"\nContent preview:\n{doc.content[:200]}...")
            print(f"\nMetadata: {json.dumps(doc.metadata, indent=2)}")
    
    print("\n" + "="*60 + "\n")


def example_2_category():
    """Example 2: Scrape and process a full category"""
    print("="*60)
    print("EXAMPLE 2: Category (Wonders - Limited to 5 pages)")
    print("="*60)
    
    scraper = Civ6WikiScraper()
    
    # Scrape wonders category (limited for demo)
    print("\n1. Scraping wonders category...")
    category_url = 'https://civilization.fandom.com/wiki/Category:Wonders_(Civ6)'
    
    # Get page URLs
    page_urls = scraper.get_category_pages(category_url)
    print(f"Found {len(page_urls)} wonder pages")
    
    # Limit to first 5 for demo
    page_urls = page_urls[:5]
    print(f"Processing first {len(page_urls)} for demo...")
    
    wonders_data = []
    for i, url in enumerate(page_urls, 1):
        print(f"  Scraping {i}/{len(page_urls)}: {url.split('/')[-1]}")
        data = scraper.extract_page_content(url, 'wonder')
        if data:
            wonders_data.append(data)
        time.sleep(1)  # Be nice to the server
    
    print(f"✓ Successfully scraped {len(wonders_data)} wonders")
    
    # Process for RAG
    print("\n2. Processing for RAG...")
    processor = Civ6RAGProcessor(chunk_size=800, chunk_overlap=100)
    
    all_documents = []
    for wonder_data in wonders_data:
        docs = processor.process_page_data(wonder_data)
        all_documents.extend(docs)
    
    print(f"✓ Generated {len(all_documents)} document chunks")
    
    # Get statistics
    stats = processor.get_statistics(all_documents)
    print(f"\n3. Statistics:")
    print(f"  - Total documents: {stats['total_documents']}")
    print(f"  - Avg content length: {stats['avg_content_length']:.0f} chars")
    
    # Save
    processor.save_processed_data(all_documents, 'example_wonders_rag.json')
    
    print("\n" + "="*60 + "\n")


def example_3_multiple_sources():
    """Example 3: Simulate combining multiple sources"""
    print("="*60)
    print("EXAMPLE 3: Multiple Sources Simulation")
    print("="*60)
    
    print("\nThis shows how you would combine multiple data sources:")
    print("(Using dummy data to demonstrate structure)")
    
    # Simulate different data sources
    all_rag_documents = []
    
    # 1. Wiki data (already processed)
    print("\n1. Civ6 Wiki data: [would be processed here]")
    wiki_docs = [
        {
            'content': 'Greece has strong cultural output...',
            'metadata': {
                'source': 'civ6_wiki',
                'category': 'civilization',
                'title': 'Greek',
                'mod': 'vanilla'
            }
        }
    ]
    all_rag_documents.extend(wiki_docs)
    
    # 2. BBG Wiki data
    print("2. BBG Wiki data: [would be processed here]")
    bbg_docs = [
        {
            'content': 'In BBG, Greece receives +2 culture...',
            'metadata': {
                'source': 'bbg_wiki',
                'category': 'civilization',
                'title': 'Greek',
                'mod': 'bbg'
            }
        }
    ]
    all_rag_documents.extend(bbg_docs)
    
    # 3. YouTube transcripts
    print("3. YouTube transcripts: [would be processed here]")
    youtube_docs = [
        {
            'content': 'The key to playing Greece is to maximize your Theater Square adjacency...',
            'metadata': {
                'source': 'youtube',
                'category': 'strategy',
                'title': 'Greece Strategy Guide',
                'creator': 'PotatoMcWhiskey',
                'video_id': 'abc123',
                'timestamp': '05:30'
            }
        }
    ]
    all_rag_documents.extend(youtube_docs)
    
    print(f"\n✓ Combined {len(all_rag_documents)} documents from 3 sources")
    print("\nSource breakdown:")
    for source in ['civ6_wiki', 'bbg_wiki', 'youtube']:
        count = sum(1 for d in all_rag_documents if d['metadata']['source'] == source)
        print(f"  - {source}: {count} documents")
    
    # Save combined data
    with open('example_combined_sources.json', 'w', encoding='utf-8') as f:
        json.dump(all_rag_documents, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Saved to example_combined_sources.json")
    
    print("\n" + "="*60 + "\n")


def example_4_metadata_filtering():
    """Example 4: Show how metadata enables smart filtering"""
    print("="*60)
    print("EXAMPLE 4: Metadata-Based Filtering")
    print("="*60)
    
    # Simulate a collection of documents
    documents = [
        {'content': 'Greece base game strategy...', 'metadata': {'category': 'civilization', 'mod': 'vanilla', 'expansion': 'base_game'}},
        {'content': 'Greece BBG strategy...', 'metadata': {'category': 'civilization', 'mod': 'bbg', 'expansion': 'base_game'}},
        {'content': 'Statue of Zeus wonder...', 'metadata': {'category': 'wonder', 'mod': 'vanilla', 'expansion': 'base_game'}},
        {'content': 'Gathering Storm mechanics...', 'metadata': {'category': 'game_concept', 'mod': 'vanilla', 'expansion': 'gathering_storm'}},
    ]
    
    print("\nExample queries with metadata filtering:\n")
    
    # Query 1: BBG-specific content
    print("1. Query: 'Greece strategy in BBG'")
    print("   Filter: mod='bbg', category='civilization'")
    filtered = [d for d in documents if d['metadata'].get('mod') == 'bbg' and 'civilization' in d['metadata'].get('category', '')]
    print(f"   Results: {len(filtered)} documents")
    for doc in filtered:
        print(f"     - {doc['content'][:50]}...")
    
    # Query 2: Gathering Storm content
    print("\n2. Query: 'What changed in Gathering Storm?'")
    print("   Filter: expansion='gathering_storm'")
    filtered = [d for d in documents if d['metadata'].get('expansion') == 'gathering_storm']
    print(f"   Results: {len(filtered)} documents")
    for doc in filtered:
        print(f"     - {doc['content'][:50]}...")
    
    # Query 3: Wonders only
    print("\n3. Query: 'Tell me about wonders'")
    print("   Filter: category='wonder'")
    filtered = [d for d in documents if d['metadata'].get('category') == 'wonder']
    print(f"   Results: {len(filtered)} documents")
    for doc in filtered:
        print(f"     - {doc['content'][:50]}...")
    
    print("\n✓ Metadata enables precise, context-aware retrieval!")
    
    print("\n" + "="*60 + "\n")


def main():
    """Run all examples"""
    print("\n")
    print("🎮 " + "="*56 + " 🎮")
    print("   CIVILIZATION VI RAG - DATA COLLECTION EXAMPLES")
    print("🎮 " + "="*56 + " 🎮")
    print("\n")
    
    examples = [
        ("Single Page", example_1_single_page),
        ("Category", example_2_category),
        ("Multiple Sources", example_3_multiple_sources),
        ("Metadata Filtering", example_4_metadata_filtering),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Run all examples")
    
    choice = input("\nSelect example (0-4): ").strip()
    
    if choice == "0":
        for name, func in examples:
            func()
            time.sleep(2)
    elif choice in ["1", "2", "3", "4"]:
        idx = int(choice) - 1
        examples[idx][1]()
    else:
        print("Invalid choice")
        return
    
    print("\n" + "="*60)
    print("✓ Examples complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review the generated JSON files")
    print("  2. Scrape additional data sources (BBG, YouTube)")
    print("  3. Build your RAG pipeline with LangChain")
    print("  4. Create the Streamlit frontend")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()