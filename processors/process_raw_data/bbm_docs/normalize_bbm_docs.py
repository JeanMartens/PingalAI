import json
import re

def parse_hierarchical_sections(text):
    """
    Parse documentation text into hierarchical sections.
    
    Returns a list of sections with:
    - title: section title
    - level: heading level (1, 2, 3, etc.)
    - content: section content
    - parent: parent section title (for hierarchy)
    """
    sections = []
    
    # Split by lines to process heading hierarchy
    lines = text.split('\n')
    
    current_section = None
    current_content = []
    parent_stack = []  # Track hierarchy
    
    for line in lines:
        line_stripped = line.strip()
        
        # Detect headings (lines that look like titles)
        # Heuristic: Short lines, possibly ending with specific patterns
        is_heading = False
        heading_level = 1
        
        # Check for common heading patterns
        if line_stripped and not line_stripped.endswith('.') and not line_stripped.endswith(','):
            # Check if it's a major heading (all caps, or starts with "Step")
            if line_stripped.isupper() or line_stripped.startswith('Step '):
                is_heading = True
                heading_level = 1
            # Check for subsection patterns (starts with "Step X.Y")
            elif re.match(r'^Step \d+\.\d+', line_stripped):
                is_heading = True
                heading_level = 2
            # Short lines that might be subheadings
            elif len(line_stripped) < 80 and line_stripped and not any(c in line_stripped for c in [',', '(', ')']):
                # Could be a heading, but be conservative
                words = line_stripped.split()
                if len(words) <= 8 and line_stripped[0].isupper():
                    is_heading = True
                    heading_level = 2
        
        if is_heading and current_section:
            # Save previous section
            if current_content:
                sections.append({
                    'title': current_section,
                    'level': heading_level,
                    'content': '\n'.join(current_content).strip(),
                    'parent': parent_stack[-1] if parent_stack else None
                })
            
            # Start new section
            current_section = line_stripped
            current_content = []
            
            # Update parent stack based on level
            if heading_level == 1:
                parent_stack = [line_stripped]
            elif heading_level == 2:
                if len(parent_stack) > 0:
                    parent_stack = [parent_stack[0], line_stripped]
                else:
                    parent_stack = [line_stripped]
        
        elif is_heading and not current_section:
            # First heading
            current_section = line_stripped
            parent_stack = [line_stripped]
        
        else:
            # Content line
            if line_stripped:  # Skip empty lines
                current_content.append(line_stripped)
    
    # Save last section
    if current_section and current_content:
        sections.append({
            'title': current_section,
            'level': heading_level,
            'content': '\n'.join(current_content).strip(),
            'parent': parent_stack[-1] if parent_stack and len(parent_stack) > 1 else None
        })
    
    return sections


def split_long_section(content, max_words=400):
    """
    Split a long section into multiple parts while preserving paragraph boundaries.
    """
    paragraphs = content.split('\n')
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for para in paragraphs:
        para_words = len(para.split())
        
        if current_word_count + para_words > max_words and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_word_count = 0
        
        current_chunk.append(para)
        current_word_count += para_words
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def normalize_bbm_documentation(data_list):
    """
    Normalize BBM documentation for RAG use.
    
    Strategy:
    1. Parse hierarchical sections from the document
    2. Create chunks that preserve context (include parent section)
    3. Split very long sections while maintaining coherence
    4. Create a table of contents chunk
    
    Creates chunks:
    - Title: Document name or section name
    - Section: Specific subsection
    - Parent Section: For hierarchy context
    - Main Content: Section content
    - Source: Metadata
    """
    out = []
    
    for data in data_list:
        title = data.get("title", "BBM Documentation")
        source = data.get("source", "bbm_docs")
        category = data.get("category", "game_mods")
        
        # Get the full text content
        sections = data.get("sections", [])
        if not sections:
            continue
        
        # Combine all content
        full_text = ""
        for sec in sections:
            content_list = sec.get("content", [])
            full_text += '\n'.join(content_list)
        
        if not full_text.strip():
            continue
        
        # Parse into hierarchical sections
        parsed_sections = parse_hierarchical_sections(full_text)
        
        # Create table of contents chunk
        if parsed_sections:
            toc_chunk = []
            toc_chunk.append(f"Title: {title}")
            toc_chunk.append("Section: Table of Contents")
            toc_chunk.append("Main Content:")
            toc_chunk.append("This document covers the following topics:")
            
            current_parent = None
            for sec in parsed_sections:
                if sec['level'] == 1:
                    toc_chunk.append(f"\n• {sec['title']}")
                    current_parent = sec['title']
                elif sec['level'] == 2 and sec.get('parent') == current_parent:
                    toc_chunk.append(f"  - {sec['title']}")
            
            toc_chunk.append(f"\nSource: {source}, {category}, documentation")
            out.append("\n".join(toc_chunk))
        
        # Create chunks for each section
        for sec in parsed_sections:
            sec_title = sec['title']
            sec_content = sec['content']
            parent = sec.get('parent')
            
            if not sec_content:
                continue
            
            # Check if section is too long
            word_count = len(sec_content.split())
            
            if word_count > 400:
                # Split long sections
                content_chunks = split_long_section(sec_content, max_words=400)
                
                for i, chunk_content in enumerate(content_chunks):
                    chunk = []
                    chunk.append(f"Title: {title}")
                    
                    if len(content_chunks) > 1:
                        chunk.append(f"Section: {sec_title} (Part {i+1}/{len(content_chunks)})")
                    else:
                        chunk.append(f"Section: {sec_title}")
                    
                    if parent and parent != sec_title:
                        chunk.append(f"Parent Section: {parent}")
                    
                    chunk.append("Main Content:")
                    chunk.append(chunk_content)
                    
                    chunk.append(f"Source: {source}, {category}, documentation")
                    out.append("\n".join(chunk))
            else:
                # Keep as single chunk
                chunk = []
                chunk.append(f"Title: {title}")
                chunk.append(f"Section: {sec_title}")
                
                if parent and parent != sec_title:
                    chunk.append(f"Parent Section: {parent}")
                
                chunk.append("Main Content:")
                chunk.append(sec_content)
                
                chunk.append(f"Source: {source}, {category}, documentation")
                out.append("\n".join(chunk))
    
    return out


def main():
    # Load the BBM documentation from plain text file
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\bbm\BBM v1.1.txt", encoding="utf-8") as f:
        text_content = f.read()
    
    # Create a data structure similar to what normalize_bbm_documentation expects
    doc_data = [{
        "title": "BBM - Better Balanced Maps v1.1",
        "source": "bbm_docs",
        "category": "game_mods",
        "sections": [{
            "heading": "Full Documentation",
            "content": [text_content]
        }]
    }]
    
    # Normalize the documentation
    chunks = normalize_bbm_documentation(doc_data)
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\bbm\documentation.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} documentation chunks")
    print(f"Saved to: data\\processed\\bbm\\documentation.json")
    
    # Print some statistics
    if chunks:
        word_counts = [len(chunk.split()) for chunk in chunks]
        print(f"\nChunk statistics:")
        print(f"  Average words per chunk: {sum(word_counts) / len(word_counts):.1f}")
        print(f"  Min words: {min(word_counts)}")
        print(f"  Max words: {max(word_counts)}")


if __name__ == "__main__":
    main()