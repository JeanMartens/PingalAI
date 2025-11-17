"""
Civ6 RAG Data Processor
Converts scraped wiki data into properly formatted chunks for vector database
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class RAGDocument:
    """Structure for a RAG-ready document chunk"""
    content: str
    metadata: Dict[str, Any]
    doc_id: str  # Unique identifier
    
    def to_dict(self):
        return asdict(self)


class Civ6RAGProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize the processor
        
        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def generate_doc_id(self, content: str, metadata: Dict) -> str:
        """Generate a unique document ID"""
        # Create a hash from content and key metadata
        hash_input = f"{content[:100]}_{metadata.get('title', '')}_{metadata.get('category', '')}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        Tries to break at sentence boundaries
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk
            end = start + self.chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending (. ! ?) within last 200 chars of chunk
                search_start = max(end - 200, start)
                search_text = text[search_start:end]
                
                # Find last sentence boundary
                for delimiter in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
                    last_delim = search_text.rfind(delimiter)
                    if last_delim != -1:
                        end = search_start + last_delim + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_page_data(self, page_data: Dict[str, Any]) -> List[RAGDocument]:
        """
        Convert a single page's data into RAG documents
        Each section becomes separate chunks with full metadata
        """
        documents = []
        
        title = page_data.get('title', '')
        category = page_data.get('category', '')
        url = page_data.get('url', '')
        source = page_data.get('source', 'civ6_wiki')
        page_metadata = page_data.get('metadata', {})
        
        # Process each section
        for section in page_data.get('sections', []):
            section_heading = section.get('heading', '')
            section_content = section.get('content', [])
            
            # Combine section content
            full_section_text = ' '.join(section_content)
            
            if not full_section_text or len(full_section_text) < 100:
                continue
            
            # Create context-rich text
            # Add title and section heading for better context
            contextualized_text = f"{title}"
            if section_heading and section_heading != 'Introduction':
                contextualized_text += f" - {section_heading}"
            contextualized_text += f"\n\n{full_section_text}"
            
            # Chunk the text
            chunks = self.chunk_text(contextualized_text)
            
            # Create document for each chunk
            for i, chunk in enumerate(chunks):
                metadata = {
                    'source': source,
                    'category': category,
                    'title': title,
                    'section': section_heading,
                    'url': url,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                }
                
                # Add any page-level metadata (like stats from infobox)
                metadata.update(page_metadata)
                
                # Detect expansion/mod (basic detection)
                if 'Rise and Fall' in full_section_text or 'R&F' in full_section_text:
                    metadata['expansion'] = 'rise_and_fall'
                elif 'Gathering Storm' in full_section_text or 'GS' in full_section_text:
                    metadata['expansion'] = 'gathering_storm'
                else:
                    metadata['expansion'] = 'base_game'
                
                doc_id = self.generate_doc_id(chunk, metadata)
                
                documents.append(RAGDocument(
                    content=chunk,
                    metadata=metadata,
                    doc_id=doc_id
                ))
        
        return documents
    
    def process_all_data(self, raw_data: Dict[str, List[Dict]]) -> List[RAGDocument]:
        """
        Process all scraped data into RAG documents
        
        Args:
            raw_data: Dictionary with categories as keys and lists of page data as values
        
        Returns:
            List of RAGDocument objects ready for vector database
        """
        all_documents = []
        
        for category, pages in raw_data.items():
            print(f"Processing category: {category} ({len(pages)} pages)")
            
            for page in pages:
                docs = self.process_page_data(page)
                all_documents.extend(docs)
            
            print(f"  Generated {len([d for d in all_documents if d.metadata['category'] == category])} documents")
        
        return all_documents
    
    def save_processed_data(self, documents: List[RAGDocument], filename: str):
        """Save processed documents to JSON"""
        data = [doc.to_dict() for doc in documents]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(documents)} documents to {filename}")
    
    def get_statistics(self, documents: List[RAGDocument]) -> Dict:
        """Get statistics about the processed documents"""
        stats = {
            'total_documents': len(documents),
            'categories': {},
            'avg_content_length': 0,
            'sources': set()
        }
        
        total_length = 0
        
        for doc in documents:
            category = doc.metadata.get('category', 'unknown')
            source = doc.metadata.get('source', 'unknown')
            
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            stats['sources'].add(source)
            total_length += len(doc.content)
        
        stats['avg_content_length'] = total_length / len(documents) if documents else 0
        stats['sources'] = list(stats['sources'])
        
        return stats


def main():
    """Example usage"""
    
    # Load scraped data
    print("Loading scraped data...")
    with open('civ6_civilizations.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Initialize processor
    processor = Civ6RAGProcessor(chunk_size=800, chunk_overlap=100)
    
    # Process data
    print("\nProcessing data into RAG format...")
    documents = processor.process_all_data(raw_data)
    
    # Get statistics
    stats = processor.get_statistics(documents)
    print("\n" + "="*50)
    print("PROCESSING STATISTICS")
    print("="*50)
    print(f"Total documents: {stats['total_documents']}")
    print(f"Average content length: {stats['avg_content_length']:.0f} characters")
    print(f"\nDocuments by category:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count}")
    print(f"\nSources: {', '.join(stats['sources'])}")
    
    # Save processed data
    processor.save_processed_data(documents, 'civ6_rag_documents.json')
    
    # Show example document
    if documents:
        print("\n" + "="*50)
        print("EXAMPLE DOCUMENT")
        print("="*50)
        example = documents[0]
        print(f"Content: {example.content[:300]}...")
        print(f"\nMetadata:")
        for key, value in example.metadata.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()