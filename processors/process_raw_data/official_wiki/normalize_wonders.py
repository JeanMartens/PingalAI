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


def extract_wonder_name(title):
    """Extract wonder name from title like 'Alhambra (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_wonders(data_list):
    """
    Normalize wonder data from Civ6 wiki for RAG use.
    
    Creates multiple chunk types:
    1. General system chunks - how wonders work (Wonder system, Natural wonder system)
    2. Specific wonder chunks - individual wonder details
    3. Strategy chunks - gameplay advice for wonders
    
    Extracts:
    - Title: Wonder name or "Wonder System" / "Natural Wonder System"
    - Section: Specific topic
    - Key Facts: Short items, stats, requirements
    - Main Content: Detailed explanations and strategy
    - Source: Metadata string
    """
    out = []
    
    for data in data_list:
        title = data.get("title", "")
        source = data.get("source", "")
        category = data.get("category", "")
        url = data.get("url", "")
        metadata = data.get("metadata", {})
        
        # Extract wonder name
        wonder_name = extract_wonder_name(title)
        
        # Determine if this is a system page or specific wonder page
        is_system_page = wonder_name in ["Wonder", "Natural wonder", "List of wonders in Civ6", "Natural wonders"]
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # === SYSTEM PAGES (General Information) ===
            if is_system_page:
                # Determine system type
                if "natural" in wonder_name.lower():
                    system_title = "Natural Wonder System"
                else:
                    system_title = "Wonder System"
                
                # Handle different section types
                if heading in ["Introduction", "Finding natural wonders[]", "Bonuses and effects[]", 
                              "Building a wonder[]", "Natural wonder picker[]"]:
                    # General mechanics and rules
                    total_words = sum(len(item.split()) for item in content_list)
                    
                    if total_words > 300:
                        # Split long sections
                        content_chunks = split_long_content(content_list, max_words=300)
                        
                        for i, chunk_content in enumerate(content_chunks):
                            chunk = []
                            chunk.append(f"Title: {system_title}")
                            
                            section_name = heading.replace('[]', '').strip()
                            if len(content_chunks) > 1:
                                chunk.append(f"Section: {section_name} (Part {i+1}/{len(content_chunks)})")
                            else:
                                chunk.append(f"Section: {section_name}")
                            
                            chunk.append("Main Content:")
                            chunk.append(chunk_content)
                            chunk.append(f"Source: {source}, {category}, game_mechanics")
                            out.append("\n".join(chunk))
                    else:
                        facts = []
                        main_content = []
                        
                        for item in content_list:
                            if len(item) < 200:
                                facts.append(item.strip())
                            else:
                                main_content.append(item.strip())
                        
                        chunk = []
                        chunk.append(f"Title: {system_title}")
                        chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                        
                        if facts:
                            chunk.append("Key Facts:")
                            for f in facts:
                                chunk.append(f"- {f}")
                        
                        if main_content:
                            chunk.append("Main Content:")
                            for m in main_content:
                                chunk.append(m)
                        
                        chunk.append(f"Source: {source}, {category}, game_mechanics")
                        out.append("\n".join(chunk))
                
                elif heading == "Strategy[]":
                    # Strategy for using wonders in general
                    total_words = sum(len(item.split()) for item in content_list)
                    
                    if total_words > 300:
                        content_chunks = split_long_content(content_list, max_words=300)
                        
                        for i, chunk_content in enumerate(content_chunks):
                            chunk = []
                            chunk.append(f"Title: {system_title}")
                            
                            if len(content_chunks) > 1:
                                chunk.append(f"Section: Strategy (Part {i+1}/{len(content_chunks)})")
                            else:
                                chunk.append("Section: Strategy")
                            
                            chunk.append("Main Content:")
                            chunk.append(chunk_content)
                            chunk.append(f"Source: {source}, {category}, strategy")
                            out.append("\n".join(chunk))
                    else:
                        chunk = []
                        chunk.append(f"Title: {system_title}")
                        chunk.append("Section: Strategy")
                        chunk.append("Main Content:")
                        for item in content_list:
                            chunk.append(item.strip())
                        chunk.append(f"Source: {source}, {category}, strategy")
                        out.append("\n".join(chunk))
                
                else:
                    # Other system sections
                    facts = []
                    main_content = []
                    
                    for item in content_list:
                        if len(item) < 200:
                            facts.append(item.strip())
                        else:
                            main_content.append(item.strip())
                    
                    chunk = []
                    chunk.append(f"Title: {system_title}")
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
            
            # === SPECIFIC WONDER PAGES ===
            else:
                # This is a specific wonder (like "Alhambra (Civ6)")
                
                if heading == "Introduction":
                    # Create overview chunk with stats and basic info
                    facts = []
                    main_content = []
                    
                    # Add metadata as key facts
                    if metadata:
                        for key, value in metadata.items():
                            if value:
                                facts.append(f"{key}: {value}")
                    
                    # Process content
                    for item in content_list:
                        if len(item) < 200:
                            facts.append(item.strip())
                        else:
                            main_content.append(item.strip())
                    
                    chunk = []
                    chunk.append(f"Title: {wonder_name}")
                    chunk.append("Section: Overview")
                    
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
                
                elif heading == "Strategy[]":
                    # Strategy for using this specific wonder
                    chunk = []
                    chunk.append(f"Title: {wonder_name}")
                    chunk.append("Section: Strategy")
                    chunk.append("Main Content:")
                    for item in content_list:
                        chunk.append(item.strip())
                    chunk.append(f"Source: {source}, {category}, strategy")
                    out.append("\n".join(chunk))
                
                elif heading == "Civilopedia entry[]":
                    # Historical background
                    total_words = sum(len(item.split()) for item in content_list)
                    
                    if total_words > 350:
                        # Split long historical entries
                        content_chunks = split_long_content(content_list, max_words=350)
                        
                        for i, chunk_content in enumerate(content_chunks):
                            chunk = []
                            chunk.append(f"Title: {wonder_name}")
                            
                            if len(content_chunks) > 1:
                                chunk.append(f"Section: Historical Background (Part {i+1}/{len(content_chunks)})")
                            else:
                                chunk.append("Section: Historical Background")
                            
                            chunk.append("Main Content:")
                            chunk.append(chunk_content)
                            chunk.append(f"Source: {source}, {category}, history")
                            out.append("\n".join(chunk))
                    else:
                        chunk = []
                        chunk.append(f"Title: {wonder_name}")
                        chunk.append("Section: Historical Background")
                        chunk.append("Main Content:")
                        for item in content_list:
                            chunk.append(item.strip())
                        chunk.append(f"Source: {source}, {category}, history")
                        out.append("\n".join(chunk))
                
                else:
                    # Other sections (version-specific effects, etc.)
                    facts = []
                    main_content = []
                    
                    for item in content_list:
                        if len(item) < 200:
                            facts.append(item.strip())
                        else:
                            main_content.append(item.strip())
                    
                    chunk = []
                    chunk.append(f"Title: {wonder_name}")
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
    # Load the wonders data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the wonders data
    chunks = normalize_wonders(data.get('wonders', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\wonders.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} wonder chunks")
    print(f"Saved to: data\\processed\\official_wiki\\wonders.json")


if __name__ == "__main__":
    main()