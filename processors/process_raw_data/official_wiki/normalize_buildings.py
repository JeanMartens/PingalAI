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


def extract_building_name(title):
    """Extract building name from title like 'Building (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_buildings(data_list):
    """
    Normalize building data from Civ6 wiki for RAG use.
    
    Creates multiple chunk types:
    1. General system chunks - how buildings work (Introduction, Requirements, Effects)
    2. Specific building chunks - individual building details
    3. Regional effect chunks - buildings that affect multiple cities
    
    Extracts:
    - Title: Building name or "Building System"
    - Section: Specific topic
    - Key Facts: Short items and bullet points
    - Main Content: Detailed explanations
    - Source: Metadata string
    """
    out = []
    
    for data in data_list:
        title = data.get("title", "")
        source = data.get("source", "")
        category = data.get("category", "")
        url = data.get("url", "")
        metadata = data.get("metadata", {})
        
        # Extract building name
        building_name = extract_building_name(title)
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # Determine chunk type and handling based on heading
            
            # === GENERAL BUILDING SYSTEM INFORMATION ===
            if building_name == "Building" and heading in ["Introduction", "Requirements[]", "Effects[]"]:
                # These explain the building system in general
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append("Title: Building System")
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
            
            # === REGIONAL EFFECTS (Special category) ===
            elif "regional" in heading.lower() or heading == "Buildings with regional effects[]":
                # Split this into overview + specific district sections
                
                # First chunk: Overview of regional effects
                overview_content = []
                district_sections = {}
                current_district = None
                
                for item in content_list:
                    # Check if this item is a district header (e.g., "Industrial Zone[]")
                    if item.strip().endswith("[]") and any(district in item for district in 
                        ["Industrial Zone", "Entertainment Complex", "Water Park", "Holy Site"]):
                        current_district = item.strip().replace("[]", "").strip()
                        district_sections[current_district] = []
                    elif current_district:
                        district_sections[current_district].append(item)
                    else:
                        overview_content.append(item)
                
                # Create overview chunk
                if overview_content:
                    total_words = sum(len(item.split()) for item in overview_content)
                    
                    if total_words > 300:
                        content_chunks = split_long_content(overview_content, max_words=300)
                        
                        for i, chunk_content in enumerate(content_chunks):
                            chunk = []
                            chunk.append("Title: Building System")
                            
                            if len(content_chunks) > 1:
                                chunk.append(f"Section: Regional Effects Overview (Part {i+1}/{len(content_chunks)})")
                            else:
                                chunk.append("Section: Regional Effects Overview")
                            
                            chunk.append("Main Content:")
                            chunk.append(chunk_content)
                            chunk.append(f"Source: {source}, {category}, regional_effects")
                            out.append("\n".join(chunk))
                    else:
                        chunk = []
                        chunk.append("Title: Building System")
                        chunk.append("Section: Regional Effects Overview")
                        chunk.append("Main Content:")
                        for item in overview_content:
                            chunk.append(item.strip())
                        chunk.append(f"Source: {source}, {category}, regional_effects")
                        out.append("\n".join(chunk))
                
                # Create separate chunks for each district's regional buildings
                for district, district_content in district_sections.items():
                    if district_content:
                        chunk = []
                        chunk.append("Title: Building System")
                        chunk.append(f"Section: Regional Effects - {district}")
                        chunk.append("Key Facts:")
                        for item in district_content:
                            if item.strip():
                                chunk.append(f"- {item.strip()}")
                        chunk.append(f"Source: {source}, {category}, regional_effects")
                        out.append("\n".join(chunk))
            
            # === SPECIFIC BUILDING INFORMATION ===
            elif building_name != "Building":
                # This is a specific building page (like "Library (Civ6)")
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {building_name}")
                chunk.append(f"Section: {heading.replace('[]', '').strip()}")
                
                # Add metadata if available
                if heading == "Introduction" and metadata:
                    if not facts:
                        chunk.append("Key Facts:")
                    else:
                        chunk.append("Key Facts:")
                    for key, value in metadata.items():
                        if value:
                            chunk.append(f"- {key}: {value}")
                
                if facts:
                    if heading != "Introduction" or not metadata:
                        chunk.append("Key Facts:")
                    for f in facts:
                        chunk.append(f"- {f}")
                
                if main_content:
                    chunk.append("Main Content:")
                    for m in main_content:
                        chunk.append(m)
                
                chunk.append(f"Source: {source}, {category}")
                out.append("\n".join(chunk))
            
            # === OTHER SECTIONS ===
            else:
                # Generic handling for any other sections
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                
                if building_name == "Building":
                    chunk.append("Title: Building System")
                else:
                    chunk.append(f"Title: {building_name}")
                
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
    # Load the buildings data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the buildings data
    chunks = normalize_buildings(data.get('buildings', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\buildings.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} building chunks")
    print(f"Saved to: data\\processed\\official_wiki\\buildings.json")


if __name__ == "__main__":
    main()