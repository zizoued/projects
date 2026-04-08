"""
Simple Flask server to proxy Yelp Fusion API requests.
Avoids CORS issues and keeps API key secure on the server side.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Get API key from environment variable
YELP_API_KEY = os.environ.get('YELP_API_KEY', '')

YELP_API_BASE = 'https://api.yelp.com/v3'

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """
    Fetch restaurants in Inner Sunset, San Francisco (94122 zip code only)
    """
    if not YELP_API_KEY:
        return jsonify({'error': 'YELP_API_KEY not set'}), 500
    
    headers = {
        'Authorization': f'Bearer {YELP_API_KEY}'
    }
    
    # Search multiple categories to capture all food establishments
    all_categories = [
        'restaurants',
        'food',
        'bakeries',
        'cafes',
        'coffee',
        'desserts',
        'juicebars',
        'bubbletea',
        'chinese',
        'japanese',
        'korean',
        'thai',
        'vietnamese',
        'indian',
        'mexican',
        'italian',
        'pizza',
        'burgers',
        'sandwiches',
        'sushi',
        'ramen',
        'noodles',
        'dimsum',
        'seafood',
        'breakfast_brunch',
        'newamerican',
        'tradamerican',
        'mediterranean',
        'mideastern',
        'tacos'
    ]
    
    all_businesses = {}
    
    try:
        # Search each category to ensure we don't miss anything
        for category in all_categories:
            params = {
                'location': '94122',
                'categories': category,
                'limit': 50,
                'sort_by': 'rating'
            }
            
            response = requests.get(
                f'{YELP_API_BASE}/businesses/search',
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            for business in data.get('businesses', []):
                # Verify the business is in zip code 94122
                zip_code = business.get('location', {}).get('zip_code', '')
                if zip_code != '94122':
                    continue
                # Use dict to dedupe by business id
                if business['id'] not in all_businesses:
                    all_businesses[business['id']] = business
        
        # Get detailed info (including hours) for each business
        restaurants = []
        for business in all_businesses.values():
            # Fetch detailed info for hours
            detail_response = requests.get(
                f'{YELP_API_BASE}/businesses/{business["id"]}',
                headers=headers
            )
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                restaurants.append({
                    'id': business['id'],
                    'name': business['name'],
                    'image_url': business.get('image_url', ''),
                    'url': business.get('url', ''),
                    'rating': business.get('rating', 0),
                    'review_count': business.get('review_count', 0),
                    'price': business.get('price', ''),
                    'phone': business.get('display_phone', ''),
                    'address': ', '.join(business['location'].get('display_address', [])),
                    'categories': [cat['title'] for cat in business.get('categories', [])],
                    'hours': detail_data.get('hours', []),
                    'is_closed': business.get('is_closed', False)
                })
        
        return jsonify({
            'restaurants': restaurants,
            'total': len(restaurants)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/restaurant/<business_id>', methods=['GET'])
def get_restaurant_details(business_id):
    """
    Get detailed info for a specific restaurant
    """
    if not YELP_API_KEY:
        return jsonify({'error': 'YELP_API_KEY not set'}), 500
    
    headers = {
        'Authorization': f'Bearer {YELP_API_KEY}'
    }
    
    try:
        response = requests.get(
            f'{YELP_API_BASE}/businesses/{business_id}',
            headers=headers
        )
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'api_key_set': bool(YELP_API_KEY)
    })


if __name__ == '__main__':
    if not YELP_API_KEY:
        print("⚠️  WARNING: YELP_API_KEY environment variable not set!")
        print("   Set it with: export YELP_API_KEY='your-api-key'")
        print("   Get your free API key at: https://www.yelp.com/developers/v3/manage_app")
        print()
    
    print("🍜 Inner Sunset Restaurants API Server")
    print("   Running at: http://localhost:5001")
    print()
    
    app.run(debug=True, port=5001)
