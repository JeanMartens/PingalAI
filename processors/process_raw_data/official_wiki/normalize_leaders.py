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


def extract_leader_name(title):
    """Extract leader name from title like 'Abraham Lincoln (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_leaders(data_list):
    """
    Normalize leader data from Civ6 wiki for RAG use.
    
    Creates multiple chunk types:
    1. Overview chunks - basic leader info with abilities and agenda
    2. Detailed approach chunks - strategic gameplay advice
    3. Civilopedia chunks - historical background (split if long)
    4. Dialogue chunks - leader-specific quotes and personality
    
    Extracts:
    - Title: Leader name
    - Section: Specific topic (Overview, Strategy, History, Dialogue)
    - Key Facts: Abilities, agenda, stats
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
        
        # Extract leader name
        leader_name = extract_leader_name(title)
        
        # Skip the general "Leaders (Civ6)" overview page
        if leader_name == "Leaders":
            continue
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # Determine chunk type and handling based on heading
            
            # === OVERVIEW CHUNKS (Introduction) ===
            if heading == "Introduction":
                facts = []
                main_content = []
                
                # Extract metadata as facts
                if metadata:
                    for key, value in metadata.items():
                        if value and key:  # Skip empty keys or values
                            facts.append(f"{key}: {value}")
                
                # Process content - first item usually has structured info
                for i, item in enumerate(content_list):
                    # First item often contains structured leader bonus/agenda info
                    if i == 0 and len(item) > 200:
                        # This is the detailed intro with abilities
                        facts.append(item.strip())
                    elif len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {leader_name}")
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
            
            # === IN-GAME MECHANICS ===
            elif heading in ["In-Game[]", "Detailed Approach[]"]:
                chunk = []
                chunk.append(f"Title: {leader_name}")
                
                if heading == "In-Game[]":
                    chunk.append("Section: Abilities and Agenda Details")
                else:
                    chunk.append("Section: Strategy and Approach")
                
                chunk.append("Main Content:")
                for item in content_list:
                    chunk.append(item.strip())
                
                chunk.append(f"Source: {source}, {category}, strategy")
                out.append("\n".join(chunk))
            
            # === INTRO FLAVOR TEXT ===
            elif heading == "Intro[]":
                chunk = []
                chunk.append(f"Title: {leader_name}")
                chunk.append("Section: Leader Introduction")
                chunk.append("Main Content:")
                for item in content_list:
                    chunk.append(item.strip())
                chunk.append(f"Source: {source}, {category}, flavor_text")
                out.append("\n".join(chunk))
            
            # === DIALOGUE/QUOTES ===
            elif heading in ["Lines[]", "Unvoiced[]", "Voiced[]"]:
                # Group dialogue into a single chunk per section
                chunk = []
                chunk.append(f"Title: {leader_name}")
                chunk.append(f"Section: Dialogue - {heading.replace('[]', '').strip()}")
                chunk.append("Key Facts:")
                for item in content_list:
                    chunk.append(f"- {item.strip()}")
                chunk.append(f"Source: {source}, {category}, dialogue")
                out.append("\n".join(chunk))
            
            # === CIVILOPEDIA (Historical Background) ===
            elif heading == "Civilopedia entry[]":
                # This is often very long - split it intelligently
                total_words = sum(len(item.split()) for item in content_list)
                
                if total_words > 400:
                    # Split into multiple chunks
                    content_chunks = split_long_content(content_list, max_words=350)
                    
                    for i, chunk_content in enumerate(content_chunks):
                        chunk = []
                        chunk.append(f"Title: {leader_name}")
                        
                        if len(content_chunks) > 1:
                            chunk.append(f"Section: Historical Background (Part {i+1}/{len(content_chunks)})")
                        else:
                            chunk.append("Section: Historical Background")
                        
                        chunk.append("Main Content:")
                        chunk.append(chunk_content)
                        chunk.append(f"Source: {source}, {category}, history")
                        out.append("\n".join(chunk))
                else:
                    # Keep as single chunk
                    chunk = []
                    chunk.append(f"Title: {leader_name}")
                    chunk.append("Section: Historical Background")
                    chunk.append("Main Content:")
                    for item in content_list:
                        chunk.append(item.strip())
                    chunk.append(f"Source: {source}, {category}, history")
                    out.append("\n".join(chunk))
            
            # === TRIVIA ===
            elif heading == "Trivia[]":
                chunk = []
                chunk.append(f"Title: {leader_name}")
                chunk.append("Section: Trivia")
                chunk.append("Key Facts:")
                for item in content_list:
                    if item.strip():
                        chunk.append(f"- {item.strip()}")
                chunk.append(f"Source: {source}, {category}, trivia")
                out.append("\n".join(chunk))
            
            # === EXTERNAL LINKS ===
            elif heading == "External links[]":
                # Usually not needed for RAG, but include if present
                chunk = []
                chunk.append(f"Title: {leader_name}")
                chunk.append("Section: External Links")
                chunk.append("Key Facts:")
                for item in content_list:
                    chunk.append(f"- {item.strip()}")
                chunk.append(f"Source: {source}, {category}, reference")
                out.append("\n".join(chunk))
            
            # === OTHER SECTIONS ===
            else:
                # Handle any other sections generically
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {leader_name}")
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
    # Load the leaders data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the leaders data
    chunks = normalize_leaders(data.get('leaders', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\leaders.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} leader chunks")
    print(f"Saved to: data\\processed\\official_wiki\\leaders.json")


if __name__ == "__main__":
    main()