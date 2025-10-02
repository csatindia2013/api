from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from your mobile app

def fetch_product_data(barcode):
    """
    Fetch product data from smartconsumer-beta.org
    
    Args:
        barcode (str): The barcode number to search
        
    Returns:
        dict: Product data containing barcode, name, and MRP
    """
    try:
        url = f"https://smartconsumer-beta.org/01/{barcode}"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product data (adjust selectors based on actual website structure)
        product_data = {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'success'
        }
        
        # Precise scraping based on smartconsumer-beta.org HTML structure from dev tools
        
        # Strategy 1: Extract product name from H1 tag (most reliable)
        # From dev tools: <h1 class="text-2xl font-bold text-gray-900 sm:text-3xl">Chakki Fresh Atta</h1>
        h1_elem = soup.find('h1', class_=re.compile(r'text-2xl.*font-bold.*text-gray-900'))
        if h1_elem:
            product_data['name'] = h1_elem.get_text(strip=True)
        
        # Strategy 2: If H1 not found, try other heading selectors
        if not product_data['name']:
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                heading_text = heading.get_text(strip=True)
                if heading_text and len(heading_text) > 3:
                    product_data['name'] = heading_text
                    break
        
        # Strategy 3: Extract from paragraph with product description
        # From dev tools: <p class="text-lg text-gray-600 font-medium">Fortune Chakki Fresh Atta 5 KG</p>
        p_elem = soup.find('p', class_=re.compile(r'text-lg.*text-gray-600.*font-medium'))
        if p_elem and not product_data['name']:
            product_data['name'] = p_elem.get_text(strip=True)
        
        # Strategy 4: Look for barcode span to confirm we're on the right page
        # From dev tools: <span class="font-mono text-gray-800 font-medium tracking-wide">8906007289085</span>
        barcode_span = soup.find('span', class_=re.compile(r'font-mono.*text-gray-800.*font-medium.*tracking-wide'))
        if barcode_span:
            found_barcode = barcode_span.get_text(strip=True)
            if found_barcode == barcode:
                print(f"✅ Confirmed barcode match: {found_barcode}")
        
        # For MRP - look for "View MRP" span
        # From dev tools: <span class="text-2xl font-bold text-gray-900 cursor-pointer">View MRP</span>
        mrp_span = soup.find('span', string=re.compile(r'View MRP', re.I))
        if mrp_span:
            product_data['mrp'] = 'View MRP (click required)'
        else:
            # Alternative: Look for span with specific classes containing "View MRP"
            mrp_spans = soup.find_all('span', class_=re.compile(r'text-2xl.*font-bold.*cursor-pointer'))
            for span in mrp_spans:
                if 'view mrp' in span.get_text(strip=True).lower():
                    product_data['mrp'] = 'View MRP (click required)'
                    break
        
        # Fallback: Look for any price patterns if "View MRP" not found
        if not product_data['mrp']:
            page_text = soup.get_text()
            price_pattern = re.search(r'₹\s*(\d+(?:\.\d{2})?)', page_text)
            if price_pattern:
                product_data['mrp'] = price_pattern.group(1)
        
        # Additional fallback for product name
        if not product_data['name']:
            # Look for any text containing product keywords
            page_text = soup.get_text()
            lines = page_text.split('\n')
            for line in lines:
                line = line.strip()
                if ('atta' in line.lower() or 'chakki' in line.lower()) and len(line) > 5:
                    product_data['name'] = line
                    break
        
        return product_data
        
    except requests.exceptions.RequestException as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Failed to fetch data: {str(e)}'
        }
    except Exception as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Error parsing data: {str(e)}'
        }

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Barcode API Server',
        'version': '1.0',
        'endpoints': {
            'GET /api/barcode/<barcode>': 'Fetch product data by barcode',
            'POST /api/barcode': 'Fetch product data by barcode (JSON body)'
        }
    })

@app.route('/api/barcode/<barcode>', methods=['GET'])
def get_barcode_data_get(barcode):
    """
    GET endpoint to fetch product data by barcode
    
    Example: GET /api/barcode/8906007289085
    """
    if not barcode or not barcode.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid barcode. Barcode must be numeric.'
        }), 400
    
    product_data = fetch_product_data(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 500
    
    return jsonify(product_data)

@app.route('/api/barcode', methods=['POST'])
def get_barcode_data_post():
    """
    POST endpoint to fetch product data by barcode
    
    Expected JSON body:
    {
        "barcode": "8906007289085"
    }
    """
    data = request.get_json()
    
    if not data or 'barcode' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing barcode in request body'
        }), 400
    
    barcode = str(data['barcode'])
    
    if not barcode.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid barcode. Barcode must be numeric.'
        }), 400
    
    product_data = fetch_product_data(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 500
    
    return jsonify(product_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

if __name__ == '__main__':
    # Run the Flask app
    # For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)

