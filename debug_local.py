"""
Debug script to test web scraping locally with detailed output
"""
import requests
from bs4 import BeautifulSoup
import re

def debug_scrape_local(barcode):
    url = f"https://smartconsumer-beta.org/01/{barcode}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔍 Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Content Length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n" + "="*60)
        print("🔍 SEARCHING FOR H1 ELEMENTS")
        print("="*60)
        
        # Search for H1 elements with our target classes
        h1_elements = soup.find_all('h1')
        print(f"Found {len(h1_elements)} H1 elements:")
        for i, h1 in enumerate(h1_elements):
            classes = h1.get('class', [])
            text = h1.get_text(strip=True)
            print(f"  H1 {i+1}: classes={classes}, text='{text}'")
            
            # Check if this matches our target class pattern
            class_str = ' '.join(classes) if classes else ''
            if re.search(r'text-2xl.*font-bold.*text-gray-900', class_str):
                print(f"    ✅ MATCHES TARGET PATTERN!")
        
        print("\n" + "="*60)
        print("🔍 SEARCHING FOR SPAN ELEMENTS WITH 'View MRP'")
        print("="*60)
        
        # Search for spans containing "View MRP"
        mrp_spans = soup.find_all('span', string=re.compile(r'View MRP', re.I))
        print(f"Found {len(mrp_spans)} spans with 'View MRP':")
        for i, span in enumerate(mrp_spans):
            classes = span.get('class', [])
            text = span.get_text(strip=True)
            print(f"  Span {i+1}: classes={classes}, text='{text}'")
        
        print("\n" + "="*60)
        print("🔍 SEARCHING FOR ALL SPANS WITH CURSOR-POINTER")
        print("="*60)
        
        # Search for spans with cursor-pointer class
        cursor_spans = soup.find_all('span', class_=re.compile(r'cursor-pointer'))
        print(f"Found {len(cursor_spans)} spans with cursor-pointer:")
        for i, span in enumerate(cursor_spans):
            classes = span.get('class', [])
            text = span.get_text(strip=True)
            print(f"  Span {i+1}: classes={classes}, text='{text}'")
        
        print("\n" + "="*60)
        print("🔍 PAGE TITLE AND META TAGS")
        print("="*60)
        
        title = soup.find('title')
        if title:
            print(f"Title: {title.get_text(strip=True)}")
        
        meta_tags = soup.find_all('meta')
        for meta in meta_tags[:10]:  # First 10 meta tags
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                print(f"Meta {name}: {content}")
        
        print("\n" + "="*60)
        print("🔍 SAMPLE PAGE TEXT (FIRST 1000 CHARS)")
        print("="*60)
        
        page_text = soup.get_text()
        print(page_text[:1000])
        
        print("\n" + "="*60)
        print("🔍 TESTING OUR SELECTORS")
        print("="*60)
        
        # Test our H1 selector
        h1_elem = soup.find('h1', class_=re.compile(r'text-2xl.*font-bold.*text-gray-900'))
        print(f"H1 selector result: {h1_elem.get_text(strip=True) if h1_elem else 'None'}")
        
        # Test our MRP selector
        mrp_span = soup.find('span', string=re.compile(r'View MRP', re.I))
        print(f"MRP span result: {mrp_span.get_text(strip=True) if mrp_span else 'None'}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_scrape_local("8906007289085")
