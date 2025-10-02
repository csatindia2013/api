"""
Debug script to test web scraping locally
"""
import requests
from bs4 import BeautifulSoup
import re

def debug_scrape(barcode):
    url = f"https://smartconsumer-beta.org/01/{barcode}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== DEBUGGING SCRAPING ===")
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print()
        
        # Print all headings
        print("=== ALL HEADINGS ===")
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            print(f"H{i+1}: {heading.get_text(strip=True)}")
        print()
        
        # Print all text containing "Chakki" or "Atta"
        print("=== TEXT CONTAINING 'CHAKKI' OR 'ATTA' ===")
        page_text = soup.get_text()
        lines = page_text.split('\n')
        for line in lines:
            if 'chakki' in line.lower() or 'atta' in line.lower():
                print(f"Found: {line.strip()}")
        print()
        
        # Print all text containing "MRP" or "₹"
        print("=== TEXT CONTAINING 'MRP' OR '₹' ===")
        for line in lines:
            if 'mrp' in line.lower() or '₹' in line:
                print(f"Found: {line.strip()}")
        print()
        
        # Print all divs with class containing "product", "name", "title"
        print("=== DIVS WITH PRODUCT/NAME/TITLE CLASSES ===")
        for div in soup.find_all('div', class_=re.compile('product|name|title', re.I)):
            print(f"Class: {div.get('class')}, Text: {div.get_text(strip=True)[:100]}")
        print()
        
        # Print all spans with class containing "product", "name", "title"
        print("=== SPANS WITH PRODUCT/NAME/TITLE CLASSES ===")
        for span in soup.find_all('span', class_=re.compile('product|name|title', re.I)):
            print(f"Class: {span.get('class')}, Text: {span.get_text(strip=True)[:100]}")
        print()
        
        # Print page title
        print("=== PAGE TITLE ===")
        title = soup.find('title')
        if title:
            print(f"Title: {title.get_text(strip=True)}")
        print()
        
        # Print all meta tags
        print("=== META TAGS ===")
        for meta in soup.find_all('meta'):
            if meta.get('name') or meta.get('property'):
                print(f"{meta.get('name', meta.get('property'))}: {meta.get('content', '')}")
        print()
        
        # Print first 500 characters of body text
        print("=== FIRST 500 CHARS OF BODY TEXT ===")
        body_text = soup.find('body')
        if body_text:
            print(body_text.get_text(strip=True)[:500])
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_scrape("8906007289085")
