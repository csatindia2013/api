from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
from product_database import get_product_info, add_product, search_products as search_db_products

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from your mobile app

def fetch_product_data(barcode):
    """
    Fetch product data using database lookup and web scraping fallback
    
    Args:
        barcode (str): The barcode number to search
        
    Returns:
        dict: Product data containing barcode, name, and MRP
    """
    try:
        print(f"🔍 Looking up barcode: {barcode}")
        
        # First, try to get from our product database
        product_info = get_product_info(barcode)
        if product_info:
            print(f"✅ Found in database: {product_info['name']} - ₹{product_info['mrp']}")
            return {
                'barcode': barcode,
                'name': product_info['name'],
                'mrp': product_info['mrp'],
                'category': product_info.get('category', ''),
                'brand': product_info.get('brand', ''),
                'status': 'success'
            }
        
        # If not in database, return proper error
        print(f"❌ Barcode {barcode} not found in database")
        
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'category': None,
            'brand': None,
            'status': 'error',
            'message': 'Product not found in database. Please add product using /api/products endpoint or scan a different barcode.'
        }
        
    except Exception as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Error: {str(e)}'
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
        return jsonify(product_data), 404  # Not Found
    
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
        return jsonify(product_data), 404  # Not Found
    
    return jsonify(product_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

@app.route('/api/search', methods=['GET'])
def search_products():
    """Search products by name or brand"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Query parameter "q" is required'
        }), 400
    
    results = search_db_products(query)
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'status': 'success'
    })

@app.route('/api/products', methods=['POST'])
def add_new_product():
    """Add new product to database"""
    data = request.get_json()
    
    if not data or 'barcode' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing barcode in request body'
        }), 400
    
    barcode = str(data['barcode'])
    name = data.get('name', f'Product {barcode}')
    mrp = data.get('mrp', '0.00')
    category = data.get('category', 'General')
    brand = data.get('brand', 'Unknown')
    
    add_product(barcode, name, mrp, category, brand)
    
    return jsonify({
        'barcode': barcode,
        'name': name,
        'mrp': mrp,
        'category': category,
        'brand': brand,
        'status': 'success',
        'message': 'Product added successfully'
    })

if __name__ == '__main__':
    # Run the Flask app
    # For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)

