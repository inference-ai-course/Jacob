import os
import pytesseract
from pdf2image import convert_from_path
import json
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import trafilatura

# Configuration
ARXIV_CATEGORY = "cs.CL"  # Example: computer science - computation and language
OUTPUT_DIR = "arxiv_ocr_output"
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
TXT_DIR = os.path.join(OUTPUT_DIR, "text")

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)

def fetch_latest_papers(category: str, max_results: int = 200) -> List[Dict]:
    """Fetch latest papers from arXiv API"""
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    
    papers = []
    for entry in soup.find_all('entry'):
        paper = {
            'url': entry.id.text,
            'title': entry.title.text.strip(),
            'authors': [author.find('name').text for author in entry.find_all('author')],
            'date': entry.published.text.split('T')[0],
            'pdf_url': None
        }
        
        # Find PDF link
        for link in entry.find_all('link'):
            if link.get('title') == 'pdf':
                paper['pdf_url'] = link.get('href')
                break
                
        papers.append(paper)
    
    return papers

def download_pdf(url: str, output_path: str) -> bool:
    """Download PDF from arXiv"""
    try:
        response = requests.get(url)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return False

def pdf_to_text(pdf_path: str, output_path: str) -> None:
    """Convert PDF to text using OCR"""
    try:
        # Convert PDF to images
        pages = convert_from_path(pdf_path, 500)
        
        # Extract text from each page
        full_text = ""
        for page in pages:
            text = pytesseract.image_to_string(page)
            full_text += text + "\n\n"
        
        # Save to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
            
    except Exception as e:
        print(f"Error processing PDF: {e}")

def process_papers(papers: List[Dict]) -> None:
    """Process all papers: download PDFs and perform OCR"""
    results = []
    
    for i, paper in enumerate(papers, 1):
        if not paper['pdf_url']:
            print(f"Skipping {paper['title']} - no PDF available")
            continue
            
        print(f"Processing paper {i}/{len(papers)}: {paper['title']}")
        
        # Generate filenames
        pdf_filename = f"paper_{i}.pdf"
        txt_filename = f"paper_{i}.txt"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        txt_path = os.path.join(TXT_DIR, txt_filename)
        
        # Download PDF
        if not os.path.exists(pdf_path):
            if not download_pdf(paper['pdf_url'], pdf_path):
                continue
        
        # Perform OCR if text file doesn't exist
        if not os.path.exists(txt_path):
            pdf_to_text(pdf_path, txt_path)
        
        # Add to results
        paper['local_pdf'] = pdf_path
        paper['local_txt'] = txt_path
        results.append(paper)
    
    # Save metadata
    with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'w') as f:
        json.dump(results, f, indent=2)

def main():
    print(f"Fetching latest papers from arXiv category: {ARXIV_CATEGORY}")
    papers = fetch_latest_papers(ARXIV_CATEGORY)
    
    print(f"Processing {len(papers)} papers...")
    process_papers(papers)
    
    print(f"Processing complete. Results saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()