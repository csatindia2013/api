"""
Test script to find the actual MRP extraction method
"""
import requests
from bs4 import BeautifulSoup
import re
import json

def test_mrp_extraction():
    barcode = "8906007289085"
    
    # Try different approaches to get MRP
    strategies = [
        f"https://smartconsumer-beta.org/01/{barcode}",
        f"https://smartconsumer-beta.org/api/product/{barcode}",
        f"https://smartconsumer-beta.org/api/barcode/{barcode}",
        f"https://smartconsumer-beta.org/data/{barcode}",
        f"https://smartconsumer-beta.org/products/{barcode}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    for i, url in enumerate(strategies, 1):
        print(f"\n🔍 Strategy {i}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {response.status_code}, Length: {len(response.content)}")
            
            # Check if it's JSON
            try:
                json_data = response.json()
                print(f"📄 JSON Response: {json_data}")
                
                # Look for price fields
                price_fields = ['mrp', 'price', 'cost', 'amount', 'value', 'selling_price', 'list_price']
                for field in price_fields:
                    if field in json_data:
                        print(f"💰 Found {field}: {json_data[field]}")
                        
            except json.JSONDecodeError:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for script tags with data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        script_text = script.string
                        
                        # Look for price patterns in scripts
                        price_patterns = [
                            r'"price":\s*"?(\d+(?:\.\d{2})?)"?',
                            r'"mrp":\s*"?(\d+(?:\.\d{2})?)"?',
                            r'"cost":\s*"?(\d+(?:\.\d{2})?)"?',
                            r'₹\s*(\d+(?:\.\d{2})?)',
                            r'Rs\.?\s*(\d+(?:\.\d{2})?)',
                            r'(\d{2,5}(?:\.\d{2})?)\s*(?:Rs|₹|rupees?)',
                        ]
                        
                        for pattern in price_patterns:
                            matches = re.findall(pattern, script_text, re.I)
                            if matches:
                                print(f"💰 Found price in script: {matches[0]}")
                        
                        # Look for JSON data in scripts
                        json_matches = re.findall(r'\{[^{}]*"price"[^{}]*\}', script_text)
                        for json_str in json_matches:
                            try:
                                data = json.loads(json_str)
                                print(f"📄 JSON in script: {data}")
                            except:
                                pass
                
                # Look for hidden input fields with prices
                inputs = soup.find_all('input', {'type': 'hidden'})
                for inp in inputs:
                    value = inp.get('value', '')
                    if re.search(r'\d{2,5}(?:\.\d{2})?', value):
                        print(f"💰 Hidden input price: {value}")
                
                # Look for data attributes
                elements = soup.find_all(attrs={"data-price": True})
                for elem in elements:
                    price = elem.get('data-price')
                    print(f"💰 Data attribute price: {price}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mrp_extraction()
