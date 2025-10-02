"""
Check the actual HTTP response from smartconsumer
"""
import requests
from bs4 import BeautifulSoup

def check_response():
    url = "https://smartconsumer-beta.org/01/8906007289085"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"🔍 Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        print(f"Headers: {dict(response.headers)}")
        print("\n" + "="*60)
        print("RAW HTML CONTENT:")
        print("="*60)
        print(response.text)
        print("="*60)
        
        # Try to find any JavaScript or API calls
        if 'script' in response.text.lower():
            print("\n🔍 Found JavaScript - content might be loaded dynamically")
        
        # Check for redirects
        if response.history:
            print(f"\n🔄 Redirects: {[r.url for r in response.history]}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_response()
