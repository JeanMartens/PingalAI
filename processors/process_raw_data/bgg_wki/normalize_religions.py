import json

def normalize_religion(data):
    """
    Normalize religion data from BBG wiki for RAG use.
    
    Extracts:
    - Title: Main document title
    - Section: Belief category and name (e.g., "Pantheon: Dance of the Aurora")
    - Key Facts: Short content items (< 200 chars)
    - Main Content: Longer descriptive text (>= 200 chars)
    - Source: Metadata string
    """
    out = []
    title = data.get("title", "")
    source = data.get("source", "")
    category = data.get("category", "")
    page_name = data.get("page_name", "")
    version = data.get("bbg_version", "")

    for sec in data.get("sections", []):
        heading = sec.get("heading", "")
        content_list = sec.get("content", [])
        facts = []
        main = []

        # Separate short facts from longer content
        for c in content_list:
            if len(c) < 200:
                facts.append(c.strip())
            else:
                main.append(c.strip())

        # Build the chunk
        chunk = []
        
        if title:
            chunk.append(f"Title: {title}")
        
        if heading:
            chunk.append(f"Section: {heading}")
        
        if facts:
            chunk.append("Key Facts:")
            for f in facts:
                chunk.append(f"- {f}")
        
        if main:
            chunk.append("Main Content:")
            for m in main:
                chunk.append(m)
        
        # Build source metadata
        meta_parts = []
        if source:
            meta_parts.append(source)
        if category:
            meta_parts.append(category)
        if page_name:
            meta_parts.append(page_name)
        if version:
            meta_parts.append(f"v{version}")
        
        if meta_parts:
            chunk.append("Source: " + ", ".join(meta_parts))

        out.append("\n".join(chunk))

    return out


def main():
    # Load the religion data
    with open(r"data\raw\bbg_wiki\bbg_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize the religion data
    chunks = normalize_religion(data.get('religion', {})[0])
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"data\processed\bbg\religion.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} religion belief chunks")
    print(f"Saved to: data\\processed\\bbg\\religion.json")


if __name__ == "__main__":
    main()