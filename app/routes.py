from app import app
from flask import request, jsonify
import requests
from bs4 import BeautifulSoup

@app.route('/')
def index():
    return "Mercadolibre Scraper API"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')  # Get search query from URL parameter
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    url = f"https://listado.mercadolibre.com.ar/{query}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data'}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    
    card_class =  "ui-search-layout__item"
    product_brand_class = "ui-search-item__brand-discoverability ui-search-item__group__element"
    final_price_container_class = "andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"
    final_price_class = "andes-money-amount__fraction"
    print("Scraping at ", url)
    products = []
    for card in soup.find_all('li', class_=card_class):  # Replace with actual class
      # print("\nPRODUCT", product, '\n')
      title = card.find('a')
      final_price = int(card.find('span', class_=final_price_container_class).find('span', class_=final_price_class).text.replace('.', ''))
      try:
          brand_element = card.find('span', class_=product_brand_class)
          brand = brand_element.text.strip() if brand_element and brand_element.text.strip() else None
      except AttributeError:
          brand = None
      
      products.append({
          'title': title.text,
          'url': title['href'],
          'final_price': final_price,
          'brand': brand
      })
    # print(products)

    return jsonify(products)

