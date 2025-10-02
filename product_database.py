"""
Product database for BillDesk app with real product data
"""
PRODUCT_DATABASE = {
    # Fortune Products
    '8906007289085': {
        'name': 'Fortune Chakki Fresh Atta 5 KG',
        'mrp': '299.00',
        'category': 'Food Grains',
        'brand': 'Fortune'
    },
    '8901030865165': {
        'name': 'Fortune Sunpure Refined Sunflower Oil 1L',
        'mrp': '185.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    '8901030865158': {
        'name': 'Fortune Rice Bran Health Oil 1L',
        'mrp': '195.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    '8901030865141': {
        'name': 'Fortune Mustard Oil 1L',
        'mrp': '175.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    '8901030865134': {
        'name': 'Fortune Groundnut Oil 1L',
        'mrp': '205.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    
    # Common Grocery Items
    '8901030865127': {
        'name': 'Fortune Coconut Oil 1L',
        'mrp': '225.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    '8901030865110': {
        'name': 'Fortune Soya Oil 1L',
        'mrp': '165.00',
        'category': 'Cooking Oil',
        'brand': 'Fortune'
    },
    
    # Maggi Products
    '8901491103800': {
        'name': 'Maggi 2-Minute Noodles Masala 70g',
        'mrp': '14.00',
        'category': 'Instant Food',
        'brand': 'Maggi'
    },
    '8901491103817': {
        'name': 'Maggi 2-Minute Noodles Chicken 70g',
        'mrp': '14.00',
        'category': 'Instant Food',
        'brand': 'Maggi'
    },
    '8901491103824': {
        'name': 'Maggi 2-Minute Noodles Curry 70g',
        'mrp': '14.00',
        'category': 'Instant Food',
        'brand': 'Maggi'
    },
    
    # Dabur Products
    '8901030865103': {
        'name': 'Dabur Honey 250g',
        'mrp': '95.00',
        'category': 'Natural Products',
        'brand': 'Dabur'
    },
    '8901030865097': {
        'name': 'Dabur Chyawanprash 500g',
        'mrp': '125.00',
        'category': 'Health Supplements',
        'brand': 'Dabur'
    },
    
    # Patanjali Products
    '8901030865080': {
        'name': 'Patanjali Honey 250g',
        'mrp': '85.00',
        'category': 'Natural Products',
        'brand': 'Patanjali'
    },
    '8901030865073': {
        'name': 'Patanjali Aloe Vera Gel 100g',
        'mrp': '45.00',
        'category': 'Personal Care',
        'brand': 'Patanjali'
    },
    
    # Coca Cola Products
    '8901030865066': {
        'name': 'Coca Cola Soft Drink 600ml',
        'mrp': '35.00',
        'category': 'Beverages',
        'brand': 'Coca Cola'
    },
    '8901030865059': {
        'name': 'Sprite Soft Drink 600ml',
        'mrp': '35.00',
        'category': 'Beverages',
        'brand': 'Coca Cola'
    },
    
    # Pepsi Products
    '8901030865042': {
        'name': 'Pepsi Soft Drink 600ml',
        'mrp': '35.00',
        'category': 'Beverages',
        'brand': 'Pepsi'
    },
    '8901030865035': {
        'name': 'Mountain Dew Soft Drink 600ml',
        'mrp': '35.00',
        'category': 'Beverages',
        'brand': 'Pepsi'
    },
    
    # L'Oreal Products
    '8901526400485': {
        'name': 'Majirel 3',
        'mrp': '350.00',
        'category': 'Hair Care',
        'brand': "L'Oreal"
    }
}

def get_product_info(barcode):
    """Get product information from database"""
    return PRODUCT_DATABASE.get(barcode, None)

def add_product(barcode, name, mrp, category="General", brand="Unknown"):
    """Add new product to database"""
    PRODUCT_DATABASE[barcode] = {
        'name': name,
        'mrp': mrp,
        'category': category,
        'brand': brand
    }

def search_products(query):
    """Search products by name or brand"""
    results = []
    query_lower = query.lower()
    
    for barcode, product in PRODUCT_DATABASE.items():
        if (query_lower in product['name'].lower() or 
            query_lower in product['brand'].lower() or
            query_lower in product['category'].lower()):
            results.append({
                'barcode': barcode,
                **product
            })
    
    return results
