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


def extract_concept_name(title):
    """Extract concept name from title like 'Adjacency bonus (Civ6)'"""
    match = re.match(r'(.+?)\s*\(Civ6\)', title)
    return match.group(1) if match else title


def normalize_game_concepts(data_list):
    """
    Normalize game concepts data from Civ6 wiki for RAG use.
    
    Game concepts are all system/mechanic explanations - no individual items.
    Each concept explains a game system like adjacency bonuses, ages, loyalty, etc.
    
    Creates focused chunks:
    - Overview chunks for introductions
    - Mechanic explanation chunks (may be split if long)
    - Sub-system chunks for complex mechanics
    
    Extracts:
    - Title: Concept name (e.g., "Adjacency Bonus", "Age System", "Loyalty")
    - Section: Specific aspect of the mechanic
    - Key Facts: Short bullet points and rules
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
        
        # Extract concept name
        concept_name = extract_concept_name(title)
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # All game concepts are system explanations
            # Determine how to handle each section
            
            if heading == "Introduction":
                # Overview of the concept
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {concept_name}")
                chunk.append("Section: Overview")
                
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
            
            elif any(keyword in heading.lower() for keyword in 
                    ["what are", "what is", "mechanics", "how it works", "how to"]):
                # Core mechanic explanations
                total_words = sum(len(item.split()) for item in content_list)
                
                if total_words > 300:
                    # Split long mechanic explanations
                    content_chunks = split_long_content(content_list, max_words=300)
                    
                    for i, chunk_content in enumerate(content_chunks):
                        chunk = []
                        chunk.append(f"Title: {concept_name}")
                        
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
                    chunk.append(f"Title: {concept_name}")
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
            
            elif "affected by" in heading.lower() or "elements" in heading.lower():
                # Lists of affected elements or subsystems
                facts = []
                main_content = []
                
                for item in content_list:
                    if len(item) < 200:
                        facts.append(item.strip())
                    else:
                        main_content.append(item.strip())
                
                chunk = []
                chunk.append(f"Title: {concept_name}")
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
                # Sub-mechanics, specific aspects, or detailed rules
                total_words = sum(len(item.split()) for item in content_list)
                
                if total_words > 300:
                    # Split long sections
                    content_chunks = split_long_content(content_list, max_words=300)
                    
                    for i, chunk_content in enumerate(content_chunks):
                        chunk = []
                        chunk.append(f"Title: {concept_name}")
                        
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
                    chunk.append(f"Title: {concept_name}")
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
    
    return out


def main():
    # Load the game concepts data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\civ6_wiki\civ6_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the game concepts data
    chunks = normalize_game_concepts(data.get('game_concepts', {}))
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\official_wiki\game_concepts.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} game concept chunks")
    print(f"Saved to: data\\processed\\official_wiki\\game_concepts.json")


if __name__ == "__main__":
    main()