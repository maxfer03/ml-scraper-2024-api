from app import app
from flask import request, jsonify
import requests
from bs4 import BeautifulSoup
import time
@app.route('/')
def index():
    # Home route that returns a string
    return "Mercadolibre Scraper API"

@app.route('/search', methods=['GET'])
def search(): 
    start_time = time.time()
    # Get the query parameter from the URL
    query = request.args.get('query', '')
    page_query = request.args.get('page', '')
    
    # If no query provided, return an error
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not page_query:
        page_query = 0
    
    # List to store the scraped products
    page_data = {
       'info': {
          'current_page': int(page_query),
          'total_pages': 0,
          'url': ''
       },
       'products': []
    }

    # Flag to indicate when the scraping should stop
    has_finished = 0
    def get_page_data(page=0):
      # Declare has_finished as nonlocal
      nonlocal has_finished
      # Append the page query if page > 0
      page_suffix = f'_Desde_{49*page}_NoIndex_True' if page > 0 else ''
      
      # URL of the page to be scraped
      url = f"https://listado.mercadolibre.com.ar/{query}{page_suffix}"
      page_data['info']['url'] = url
      # Send a GET request to the URL
      response = requests.get(url)
      print(f'scraping at page {page}: {url}')
      
      # If the request was not successful, stop scraping and return an error
      if response.status_code != 200:
          has_finished = 1
          print('Failed to fetch data')
          return jsonify({'error': 'Failed to fetch data'}), 500

      # Parse the HTML content of the page
      soup = BeautifulSoup(response.content, 'html.parser')

      # CSS classes of the elements to be scraped
      card_class =  "ui-search-layout__item"
      product_brand_class = "ui-search-item__brand-discoverability ui-search-item__group__element"
      final_price_container_class = "andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"
      final_price_class = "andes-money-amount__fraction"
      
      total_pages_class = "andes-pagination__page-count"

      

      try:
         page_data['info']['total_pages'] = int(soup.find('li', class_=total_pages_class).text.split(' ')[1])
      except AttributeError:
         page_data['info']['total_pages'] = 1



      
      # Find and iterate over all the product cards
      scraped_products = soup.find_all('li', class_=card_class)
      for card in scraped_products:
        # Find the title, URL, final price, and brand of the product
        title = card.find('a')
        final_price = int(card.find('span', class_=final_price_container_class).find('span', class_=final_price_class).text.replace('.', ''))
        try:
            brand_element = card.find('span', class_=product_brand_class)
            brand = brand_element.text.strip() if brand_element and brand_element.text.strip() else None
        except AttributeError:
            brand = None
        
        # Append the product to the list
        page_data['products'].append({
            'title': title.text,
            'url': title['href'],
            'final_price': final_price,
            'brand': brand
        })
      
      total_pages = soup.find('li', class_=total_pages_class)
      
      print("FINISHED Scraping at ", url)

      
    get_page_data(int(page_query))



    # Return the list of products as JSON
    if len(page_data['products']) > 0:
      return jsonify(page_data)
    else:
      return jsonify({'error': 'No items found'}), 404
