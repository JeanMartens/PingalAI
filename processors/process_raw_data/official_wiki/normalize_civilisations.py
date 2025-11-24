import json
import re

def split_long_content(content_list, max_words=300):
    """
    Split long content blocks into smaller semantic chunks.
    Tries to keep paragraphs together when possible.
    """
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for item in content_list:
        word_count = len(item.split())
        
        # If adding this item would exceed max_words, save current chunk and start new
        if current_word_count + word_count > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_word_count = 0
        
        current_chunk.append(item)
        current_word_count += word_count
    
    # Add remaining content
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def extract_civ_name(title):
    """Extract civilization name from title like 'American (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_civilizations(data_list):
    """
    Normalize civilization data from Civ6 wiki for RAG use.
    
    Creates multiple chunk types:
    1. Overview chunks - basic civ info
    2. Leader ability chunks - each leader's specific abilities
    3. Strategy chunks - gameplay advice split semantically
    4. Unit/Building chunks - unique components
    
    Extracts:
    - Title: Civilization name
    - Section: Specific topic (Overview, Leader name, Strategy type, etc.)
    - Key Facts: Short metadata and stats
    - Main Content: Strategic advice and descriptions
    - Source: Metadata string
    """
    out = []
    
    for data in data_list:
        title = data.get("title", "")
        source = data.get("source", "")
        category = data.get("category", "")
        url = data.get("url", "")
        metadata = data.get("metadata", {})
        
        # Extract civilization name
        civ_name = extract_civ_name(title)
        
        # Skip the general "Civilizations (Civ6)" overview page
        if civ_name == "Civilizations":
            continue
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # Determine chunk type and handling based on heading
            
            # === OVERVIEW CHUNKS ===
            if heading == "Introduction":
                # Split intro into overview and ability details
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {civ_name}")
                chunk.append("Section: Overview")
                
                # Add metadata as key facts if available
                if metadata:
                    chunk.append("Key Facts:")
                    for key, value in metadata.items():
                        if value:
                            chunk.append(f"- {key}: {value}")
                
                # Add short facts
                if facts:
                    if not metadata:
                        chunk.append("Key Facts:")
                    for f in facts:
                        chunk.append(f"- {f}")
                
                if main_content:
                    chunk.append("Main Content:")
                    for m in main_content:
                        chunk.append(m)
                
                chunk.append(f"Source: {source}, {category}")
                out.append("\n".join(chunk))
            
            # === LEADER ABILITY CHUNKS ===
            elif any(leader_keyword in heading.lower() for leader_keyword in 
                    ['roosevelt', 'lincoln', 'corollary', 'emancipation', 'antiquities']):
                # These are leader-specific abilities or strategies
                
                # If content is very long, split it semantically
                total_words = sum(len(item.split()) for item in content_list)
                
                if total_words > 300:
                    # Split into smaller chunks
                    content_chunks = split_long_content(content_list, max_words=300)
                    
                    for i, chunk_content in enumerate(content_chunks):
                        chunk = []
                        chunk.append(f"Title: {civ_name}")
                        
                        # Add part number if split into multiple chunks
                        section_name = heading.replace('[]', '').strip()
                        if len(content_chunks) > 1:
                            chunk.append(f"Section: {section_name} (Part {i+1}/{len(content_chunks)})")
                        else:
                            chunk.append(f"Section: {section_name}")
                        
                        chunk.append("Main Content:")
                        chunk.append(chunk_content)
                        chunk.append(f"Source: {source}, {category}, leader_ability")
                        out.append("\n".join(chunk))
                else:
                    # Keep as single chunk
                    chunk = []
                    chunk.append(f"Title: {civ_name}")
                    chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                    chunk.append("Main Content:")
                    for item in content_list:
                        chunk.append(item.strip())
                    chunk.append(f"Source: {source}, {category}, leader_ability")
                    out.append("\n".join(chunk))
            
            # === STRATEGY CHUNKS ===
            elif 'strategy' in heading.lower() or heading in ['Vanilla version[]', 'Rise and Fall & Gathering Storm[]']:
                # These are strategic advice sections
                
                total_words = sum(len(item.split()) for item in content_list)
                
                if total_words > 300:
                    content_chunks = split_long_content(content_list, max_words=300)
                    
                    for i, chunk_content in enumerate(content_chunks):
                        chunk = []
                        chunk.append(f"Title: {civ_name}")
                        
                        section_name = heading.replace('[]', '').strip()
                        if len(content_chunks) > 1:
                            chunk.append(f"Section: Strategy - {section_name} (Part {i+1}/{len(content_chunks)})")
                        else:
                            chunk.append(f"Section: Strategy - {section_name}")
                        
                        chunk.append("Main Content:")
                        chunk.append(chunk_content)
                        chunk.append(f"Source: {source}, {category}, strategy")
                        out.append("\n".join(chunk))
                else:
                    chunk = []
                    chunk.append(f"Title: {civ_name}")
                    chunk.append(f"Section: Strategy - {heading.replace('[]', '').strip()}")
                    chunk.append("Main Content:")
                    for item in content_list:
                        chunk.append(item.strip())
                    chunk.append(f"Source: {source}, {category}, strategy")
                    out.append("\n".join(chunk))
            
            # === UNIQUE UNIT/BUILDING CHUNKS ===
            elif heading in ['P-51 Mustang[]', 'Film Studio[]', 'Rough Rider[]'] or \
                 any(keyword in heading.lower() for keyword in ['unit[]', 'building[]', 'infrastructure[]']):
                # Unique components
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 150:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {civ_name}")
                chunk.append(f"Section: Unique Component - {heading.replace('[]', '').strip()}")
                
                if facts:
                    chunk.append("Key Facts:")
                    for f in facts:
                        chunk.append(f"- {f}")
                
                if main_content:
                    chunk.append("Main Content:")
                    for m in main_content:
                        chunk.append(m)
                
                chunk.append(f"Source: {source}, {category}, unique_component")
                out.append("\n".join(chunk))
            
            # === VICTORY TYPE & COUNTER STRATEGY CHUNKS ===
            elif 'victory' in heading.lower() or 'counter' in heading.lower():
                chunk = []
                chunk.append(f"Title: {civ_name}")
                chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                chunk.append("Main Content:")
                for item in content_list:
                    chunk.append(item.strip())
                chunk.append(f"Source: {source}, {category}, gameplay_advice")
                out.append("\n".join(chunk))
            
            # === OTHER CHUNKS (Civilopedia, Trivia, etc.) ===
            else:
                # For remaining sections, use standard approach
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {civ_name}")
                chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                
                if facts:
                    chunk.append("Key Facts:")
                    for f in facts:
                        chunk.append(f"- {f}")
                
                if main_content:
                    chunk.append("Main Content:")
                    for m in main_content:
                        chunk.append(m)
                
                chunk.append(f"Source: {source}, {category}")
                out.append("\n".join(chunk))
    
    return out


def main():
    # Load the civilization data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the civilization data
    chunks = normalize_civilizations(data.get('civilizations', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\civilizations.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} civilization chunks")
    print(f"Saved to: data\\processed\\civ6\\civilizations.json")


if __name__ == "__main__":
    main()