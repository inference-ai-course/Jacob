import json
import jsonlines
from langdetect import detect
from datasketch import MinHash, MinHashLSH
import re
from typing import List, Dict, Any

# Constants
SIMILARITY_THRESHOLD = 0.7
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
    'phone': r'\b(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'
}

def load_data(task1_json: str, task2_json: str, task3_jsonl: str) -> List[Dict[str, Any]]:
    """Load data from all three task outputs"""
    combined_data = []
    
    # Load Task 1 data
    with open(task1_json, 'r') as f:
        combined_data.extend(json.load(f))
    
    # Load Task 2 data
    with open(task2_json, 'r') as f:
        combined_data.extend(json.load(f))
    
    # Load Task 3 data
    with open(task3_jsonl, 'r') as f:
        for line in jsonlines.Reader(f):
            combined_data.append(line)
    
    return combined_data

def detect_language(text: str) -> str:
    """Detect language of text"""
    try:
        return detect(text)
    except:
        return "unknown"

def remove_pii(text: str) -> str:
    """Remove personally identifiable information"""
    for pattern in PII_PATTERNS.values():
        text = re.sub(pattern, '[REDACTED]', text)
    return text

def remove_repetitive_ngrams(text: str, n: int = 3) -> str:
    """Remove repetitive n-grams"""
    words = text.split()
    seen_ngrams = set()
    cleaned_words = []
    
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        if ngram in seen_ngrams:
            continue
        seen_ngrams.add(ngram)
        cleaned_words.append(words[i])
    
    # Add remaining words
    if len(words) >= n:
        cleaned_words.extend(words[-(n-1):])
    else:
        cleaned_words.extend(words[len(cleaned_words):])
    
    return ' '.join(cleaned_words)

def clean_html(text: str) -> str:
    """Basic HTML tag removal"""
    return re.sub(r'<[^>]+>', '', text)

def process_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply all cleaning steps to the data"""
    processed = []
    
    for item in data:
        # Get text to process (prioritize abstract, then title, then content)
        text = item.get('abstract', '') or item.get('title', '') or item.get('content', '')
        
        # Skip if no text
        if not text.strip():
            continue
            
        # Clean HTML
        text = clean_html(text)
        
        # Detect language
        lang = detect_language(text)
        if lang != 'en':  # Assuming we want English content
            continue
            
        # Remove PII
        text = remove_pii(text)
        
        # Remove repetitive n-grams
        text = remove_repetitive_ngrams(text)
        
        # Update item with cleaned data
        cleaned_item = item.copy()
        if 'abstract' in cleaned_item:
            cleaned_item['abstract'] = text
        elif 'content' in cleaned_item:
            cleaned_item['content'] = text
        else:
            cleaned_item['title'] = text
            
        processed.append(cleaned_item)
    
    return processed

def deduplicate_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove near-duplicate documents using MinHashLSH"""
    lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=128)
    minhashes = {}
    
    # Create MinHashes for all documents
    for idx, item in enumerate(data):
        text = item.get('abstract', '') or item.get('title', '') or item.get('content', '')
        words = text.lower().split()
        
        mh = MinHash(num_perm=128)
        for word in words:
            mh.update(word.encode('utf-8'))
        
        minhashes[idx] = mh
        lsh.insert(idx, mh)
    
    # Find duplicates
    duplicates = set()
    for idx in minhashes:
        if idx in duplicates:
            continue
        results = lsh.query(minhashes[idx])
        if len(results) > 1:
            # Keep the first one, mark others as duplicates
            for dup_idx in results[1:]:
                duplicates.add(dup_idx)
    
    # Return only non-duplicates
    return [data[i] for i in range(len(data)) if i not in duplicates]

def export_to_txt(data: List[Dict[str, Any]], filename: str):
    """Export data to plain text format"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"Title: {item.get('title', 'N/A')}\n")
            f.write(f"Authors: {', '.join(item.get('authors', ['N/A']))}\n")
            f.write(f"Date: {item.get('date', 'N/A')}\n")
            f.write(f"URL: {item.get('url', 'N/A')}\n")
            f.write(f"Abstract/Content:\n{item.get('abstract', item.get('content', 'N/A'))}\n")
            f.write("\n" + "="*80 + "\n\n")

def export_to_md(data: List[Dict[str, Any]], filename: str):
    """Export data to Markdown format"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"## {item.get('title', 'N/A')}\n\n")
            f.write(f"**Authors:** {', '.join(item.get('authors', ['N/A']))}  \n")
            f.write(f"**Date:** {item.get('date', 'N/A')}  \n")
            f.write(f"**URL:** [{item.get('url', 'N/A')}]({item.get('url', 'N/A')})  \n\n")
            f.write(f"**Abstract/Content:**  \n\n{item.get('abstract', item.get('content', 'N/A'))}\n\n")
            f.write("---\n\n")

def main():
    # Load data from all tasks
    data = load_data('task1_output.json', 'task2_output.json', 'task3_output.jsonl')
    
    # Process data (clean, filter, etc.)
    processed_data = process_data(data)
    
    # Deduplicate data
    final_data = deduplicate_data(processed_data)
    
    # Export results
    export_to_txt(final_data, 'processed_results.txt')
    export_to_md(final_data, 'processed_results.md')
    
    print(f"Processing complete. Saved {len(final_data)} documents.")
    print("Files created: processed_results.txt, processed_results.md")

if __name__ == "__main__":
    main()