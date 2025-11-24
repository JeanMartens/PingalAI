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


def extract_district_name(title):
    """Extract district name from title like 'Acropolis (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_districts(data_list):
    """
    Normalize district data from Civ6 wiki for RAG use.
    
    Creates multiple chunk types:
    1. General system chunks - how districts work
    2. Specific district chunks - individual district details
    3. Strategy chunks - gameplay advice for districts
    
    Extracts:
    - Title: District name or "District System"
    - Section: Specific topic
    - Key Facts: Short items, stats, requirements, adjacency bonuses
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
        
        # Extract district name
        district_name = extract_district_name(title)
        
        # Determine if this is a system page or specific district page
        is_system_page = district_name in ["District", "List of districts in Civ6"]
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # === SYSTEM PAGES (General Information) ===
            if is_system_page:
                system_title = "District System"
                
                # Handle different section types
                if heading in ["Introduction", "What is a district?[]", "What does a district do?[]", 
                              "Building a district[]", "Basic requirements[]", "Suitable locations[]"]:
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
            
            # === SPECIFIC DISTRICT PAGES ===
            else:
                # This is a specific district (like "Acropolis (Civ6)")
                
                if heading == "Introduction":
                    # Create overview chunk with stats and basic info
                    facts = []
                    main_content = []
                    
                    # Add metadata as key facts
                    if metadata:
                        for key, value in metadata.items():
                            if value:
                                facts.append(f"{key}: {value}")
                    
                    # Process content - many have structured stat blocks
                    for item in content_list:
                        # Check if this is a stat line (short and likely contains numbers or yields)
                        if len(item) < 150 and (any(char.isdigit() for char in item) or 
                                               any(keyword in item.lower() for keyword in 
                                                   ['cost', 'yield', 'bonus', 'point', 'adjacency', 'slot'])):
                            facts.append(item.strip())
                        elif len(item) < 200:
                            facts.append(item.strip())
                        else:
                            main_content.append(item.strip())
                    
                    chunk = []
                    chunk.append(f"Title: {district_name}")
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
                
                elif heading in ["Buildings[]", "Projects[]"]:
                    # List of buildings or projects available in this district
                    chunk = []
                    chunk.append(f"Title: {district_name}")
                    chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                    chunk.append("Key Facts:")
                    for item in content_list:
                        if item.strip():
                            chunk.append(f"- {item.strip()}")
                    chunk.append(f"Source: {source}, {category}")
                    out.append("\n".join(chunk))
                
                elif heading == "Strategy[]":
                    # Strategy for using this specific district
                    total_words = sum(len(item.split()) for item in content_list)
                    
                    if total_words > 300:
                        # Split long strategy sections
                        content_chunks = split_long_content(content_list, max_words=300)
                        
                        for i, chunk_content in enumerate(content_chunks):
                            chunk = []
                            chunk.append(f"Title: {district_name}")
                            
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
                        chunk.append(f"Title: {district_name}")
                        chunk.append("Section: Strategy")
                        chunk.append("Main Content:")
                        for item in content_list:
                            chunk.append(item.strip())
                        chunk.append(f"Source: {source}, {category}, strategy")
                        out.append("\n".join(chunk))
                
                elif heading == "Civilopedia entry[]":
                    # Historical/flavor text
                    chunk = []
                    chunk.append(f"Title: {district_name}")
                    chunk.append("Section: Historical Background")
                    chunk.append("Main Content:")
                    for item in content_list:
                        chunk.append(item.strip())
                    chunk.append(f"Source: {source}, {category}, history")
                    out.append("\n".join(chunk))
                
                else:
                    # Other sections (version-specific mechanics, etc.)
                    facts = []
                    main_content = []
                    
                    for item in content_list:
                        if len(item) < 200:
                            facts.append(item.strip())
                        else:
                            main_content.append(item.strip())
                    
                    chunk = []
                    chunk.append(f"Title: {district_name}")
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
    # Load the districts data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the districts data
    chunks = normalize_districts(data.get('districts', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\districts.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} district chunks")
    print(f"Saved to: data\\processed\\official_wiki\\districts.json")


if __name__ == "__main__":
    main()