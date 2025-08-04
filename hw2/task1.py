import requests
from bs4 import BeautifulSoup
import trafilatura
import pytesseract
from PIL import Image
import json
import io
import time
from datetime import datetime
import os

# Configuration
ARXIV_API_URL = "http://export.arxiv.org/api/query"
CATEGORY = "cs.CL"  # Example category (Computing Science - Computation and Language)
MAX_RESULTS = 200  # Number of papers to fetch
OUTPUT_FILE = "arxiv_papers.json"

# Ensure output directory exists
os.makedirs("screenshots", exist_ok=True)

def fetch_latest_papers(category, max_results=200):
    """Fetch latest papers from arXiv API"""
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }
    
    response = requests.get(ARXIV_API_URL, params=params)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'xml')
    entries = soup.find_all('entry')
    
    papers = []
    for entry in entries:
        paper = {
            "url": entry.id.text,
            "title": entry.title.text.strip(),
            "authors": [author.find('name').text for author in entry.find_all('author')],
            "date": entry.published.text,
            "pdf_url": None
        }
        
        # Find PDF link
        for link in entry.find_all('link'):
            if link.get('title') == 'pdf':
                paper['pdf_url'] = link.get('href')
                break
                
        papers.append(paper)
    
    return papers

def scrape_abs_page(url):
    """Scrape the abstract page and extract content using trafilatura"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract with trafilatura
        extracted = trafilatura.extract(response.text, include_links=False, output_format='json')
        if extracted:
            return json.loads(extracted)
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def extract_text_from_screenshot(url):
    """Take a screenshot of the page and extract text using OCR"""
    try:
        # In a real implementation, you would use selenium/playwright to take a screenshot
        # For this example, we'll simulate it by fetching the page and pretending to OCR
        
        # This is a placeholder - actual implementation would require:
        # 1. Using selenium/playwright to take screenshot
        # 2. Saving the image
        # 3. Running OCR on it
        
        # For demo purposes, we'll just return None
        return None
        
        # Example of what the real code might look like:
        """
        from selenium import webdriver
        from PIL import Image
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Take screenshot
        screenshot_path = f"screenshots/{url.split('/')[-1]}.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        
        # Extract text with OCR
        image = Image.open(screenshot_path)
        text = pytesseract.image_to_string(image)
        return text
        """
    except Exception as e:
        print(f"OCR failed for {url}: {e}")
        return None

def process_papers(papers):
    """Process each paper to extract abstract and additional data"""
    results = []
    
    for paper in papers:
        print(f"Processing: {paper['title']}")
        
        # Scrape abstract page
        abs_data = scrape_abs_page(paper['url'])
        
        # Try OCR as fallback if trafilatura fails
        abstract = None
        if abs_data and abs_data.get('text'):
            abstract = abs_data['text']
        else:
            ocr_text = extract_text_from_screenshot(paper['url'])
            if ocr_text:
                abstract = ocr_text
        
        # Format date
        try:
            date_obj = datetime.strptime(paper['date'], '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except:
            formatted_date = paper['date']
        
        result = {
            "url": paper['url'],
            "title": paper['title'],
            "abstract": abstract,
            "authors": paper['authors'],
            "date": formatted_date,
            "pdf_url": paper['pdf_url']
        }
        
        results.append(result)
        time.sleep(1)  # Be polite to arXiv servers
    
    return results

def save_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print(f"Fetching latest {MAX_RESULTS} papers from arXiv category {CATEGORY}")
    papers = fetch_latest_papers(CATEGORY, MAX_RESULTS)
    
    print(f"Processing {len(papers)} papers...")
    processed_data = process_papers(papers)
    
    print(f"Saving results to {OUTPUT_FILE}")
    save_to_json(processed_data, OUTPUT_FILE)
    
    print("Done!")

if __name__ == "__main__":
    main()