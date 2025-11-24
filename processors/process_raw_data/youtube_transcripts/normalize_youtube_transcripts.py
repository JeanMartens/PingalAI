import json
import re

def clean_transcript(text):
    """
    Remove common transcript artifacts and clean up text.
    """
    # Remove repeated words (common in auto-generated transcripts)
    # e.g., "the the" -> "the"
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def chunk_by_words(text, target_words=250, overlap=50):
    """
    Fallback: chunk by word count with overlap.
    Used when sentence splitting fails (no punctuation).
    """
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + target_words
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += (target_words - overlap)
    
    return chunks


def chunk_by_sentences(text, target_words=250, overlap_sentences=2):
    """
    Chunk text by sentences with overlap for context continuity.
    
    Args:
        text: The transcript text to chunk
        target_words: Target number of words per chunk
        overlap_sentences: Number of sentences to overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Split into sentences (improved regex for transcripts)
    # Looks for sentence endings followed by space and capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Fallback if no proper sentences detected
    if len(sentences) == 1:
        return chunk_by_words(text, target_words, overlap=50)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_words = len(sentence.split())
        
        # If adding this sentence would exceed target, save current chunk
        if current_word_count + sentence_words > target_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            
            # Add overlap: keep last N sentences for context
            if len(current_chunk) >= overlap_sentences:
                current_chunk = current_chunk[-overlap_sentences:]
                current_word_count = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk = []
                current_word_count = 0
        
        current_chunk.append(sentence)
        current_word_count += sentence_words
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def normalize_youtube_transcripts(data_list):
    """
    Normalize YouTube transcript data for RAG use.
    
    Strategy:
    1. Clean the transcript (remove filler, repetition)
    2. Chunk by sentences with target size ~250 words
    3. Add overlap for context continuity
    4. Include video metadata in each chunk
    
    Creates chunks:
    - Title: Video title
    - Section: Part X/Y
    - Main Content: Chunk text
    - Source: youtube, category, channel
    - Video: URL
    """
    out = []
    
    for data in data_list:
        title = data.get("title", "")
        url = data.get("url", "")
        source = data.get("source", "")
        category = data.get("category", "")
        metadata = data.get("metadata", {})
        
        # Extract metadata
        channel = metadata.get("channel", "")
        video_id = metadata.get("video_id", "")
        
        for sec in data.get("sections", []):
            heading = sec.get("heading", "")
            content_list = sec.get("content", [])
            
            if not content_list:
                continue
            
            # Combine all content into one transcript
            full_transcript = ' '.join(content_list)
            
            # Clean up transcript
            full_transcript = clean_transcript(full_transcript)
            
            # Skip if transcript is too short
            if len(full_transcript.split()) < 50:
                continue
            
            # Chunk with sentence awareness and overlap
            text_chunks = chunk_by_sentences(
                full_transcript, 
                target_words=250, 
                overlap_sentences=2
            )
            
            # Create a chunk entry for each text chunk
            for i, chunk_text in enumerate(text_chunks):
                chunk = []
                
                # Title
                chunk.append(f"Title: {title}")
                
                # Section with part number
                chunk.append(f"Section: Part {i+1}/{len(text_chunks)}")
                
                # Main content
                chunk.append("Main Content:")
                chunk.append(chunk_text)
                
                # Build source metadata
                meta_parts = []
                if source:
                    meta_parts.append(source)
                if category:
                    meta_parts.append(category)
                if channel:
                    meta_parts.append(channel)
                
                if meta_parts:
                    chunk.append(f"Source: {', '.join(meta_parts)}")
                
                # Add video URL for reference
                if url:
                    chunk.append(f"Video: {url}")
                
                out.append("\n".join(chunk))
    
    return out


def main():
    # Load the YouTube transcript data
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\raw\youtube\youtube_transcripts.json", encoding="utf-8") as f:
        data = json.load(f)
    
    # Normalize the YouTube transcripts
    video_data = data.get('youtube_strategy', [])
    
    chunks = normalize_youtube_transcripts(video_data)
    
    # Save as list of dictionaries with "text" key
    saved = [{"text": c} for c in chunks]
    
    with open(r"C:\Users\jeanb\Documents\misc-code\PingalAI\data\processed\youtube\transcripts.json", "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(chunks)} transcript chunks")
    print(f"Saved to: data\\processed\\youtube\\transcripts.json")
    
    # Print statistics
    if chunks:
        word_counts = [len(chunk.split()) for chunk in chunks]
        print(f"\nChunk statistics:")
        print(f"  Average words per chunk: {sum(word_counts) / len(word_counts):.1f}")
        print(f"  Min words: {min(word_counts)}")
        print(f"  Max words: {max(word_counts)}")


if __name__ == "__main__":
    main()