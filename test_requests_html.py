"""
Test requests-html automatic scraping for Majirel 3
"""
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re

def test_auto_scrape():
    barcode = "8901526400485"  # Majirel 3
    url = f"https://smartconsumer-beta.org/01/{barcode}"
    
    print(f"🔍 Testing: {url}")
    
    try:
        session = HTMLSession()
        print("🌐 Fetching page...")
        response = session.get(url, timeout=30)
        
        print("⏳ Rendering JavaScript...")
        response.html.render(timeout=20, sleep=3)
        
        html = response.html.html
        print(f"✅ Rendered! Size: {len(html)} bytes")
        
        # Parse
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find H1
        print("\n📋 Product Name:")
        for h1 in soup.find_all('h1'):
            text = h1.get_text(strip=True)
            if text and 'smart consumer' not in text.lower():
                print(f"  ✅ {text}")
        
        # Find MRP
        print("\n💰 Price Info:")
        for span in soup.find_all('span'):
            text = span.get_text(strip=True)
            if 'mrp' in text.lower() or '₹' in text:
                print(f"  {text}")
        
        session.close()
        print("\n✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auto_scrape()
