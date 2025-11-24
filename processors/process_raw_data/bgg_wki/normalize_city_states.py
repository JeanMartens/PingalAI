import json

def normalize_city_states(data):
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

        for c in content_list:
            if len(c) < 200:
                facts.append(c.strip())
            else:
                main.append(c.strip())

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

    with open(r"data\raw\bbg_wiki\bbg_complete_data.json", encoding="utf-8") as f:
        data = json.load(f)


    chunks = normalize_city_states(data.get('city_state', {})[0])
    saved = [{"text": c} for c in chunks]
    with open(r"data\processed\bbg\city_states.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()