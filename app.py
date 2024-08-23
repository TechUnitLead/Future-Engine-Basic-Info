from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)
CRUNCHBASE_API_KEY = '37286dd10ce67e48d6daffe9bb336977'

def get_field(data, field):
    """ Helper function to safely extract fields from the API response. """
    if isinstance(data.get(field), dict):
        return data.get(field, {}).get('value', 'N/A')
    return data.get(field, 'N/A')

def format_url(url, prefix, default='N/A'):
    """ Helper function to format URLs properly. """
    if url == 'N/A':
        return default
    url = url.strip()
    if not re.match(r'^https?://', url):
        url = f"{prefix}{url}"
    return url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    company_name = request.form['company'].strip().lower()
    url = f"https://api.crunchbase.com/api/v4/entities/organizations/{company_name}"
    params = {
        'user_key': CRUNCHBASE_API_KEY,
        'field_ids': 'short_description,created_at,updated_at,facebook,linkedin,location_identifiers,stock_exchange_symbol,stock_symbol,twitter,website_url'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json().get('properties', {})
        print(data)  # Debugging line to check the response structure
        
        # Extract fields
        short_description = get_field(data, 'short_description')
        created_at = get_field(data, 'created_at')
        updated_at = get_field(data, 'updated_at')
        
        # Extract and format URLs
        facebook = format_url(get_field(data, 'facebook'), 'https://www.facebook.com/', 'N/A')
        linkedin = format_url(get_field(data, 'linkedin'), 'https://www.linkedin.com/company/', 'N/A')
        twitter = format_url(get_field(data, 'twitter'), 'https://twitter.com/', 'N/A')
        website = format_url(get_field(data, 'website_url'), 'https://', 'N/A')
        
        stock_exchange_symbol = get_field(data, 'stock_exchange_symbol')
        stock_symbol = get_field(data, 'stock_symbol')

        # Extract location
        locations = data.get('location_identifiers', [])
        location_name = ', '.join(loc['value'] for loc in locations) if locations else 'N/A'

        # Create result
        result = {
            'short_description': short_description if short_description != 'N/A' else 'N/A',
            'created_at': created_at if created_at != 'N/A' else 'N/A',
            'updated_at': updated_at if updated_at != 'N/A' else 'N/A',
            'facebook': facebook if facebook != 'N/A' else 'N/A',
            'linkedin': linkedin if linkedin != 'N/A' else 'N/A',
            'location': location_name if location_name != 'N/A' else 'N/A',
            'stock_exchange_symbol': stock_exchange_symbol if stock_exchange_symbol != 'N/A' else 'N/A',
            'stock_symbol': stock_symbol if stock_symbol != 'N/A' else 'N/A',
            'twitter': twitter if twitter != 'N/A' else 'N/A',
            'website': website if website != 'N/A' else 'N/A'
        }
        return jsonify(result)
    else:
        return jsonify({'error': 'Company not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
