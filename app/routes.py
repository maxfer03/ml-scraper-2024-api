from app import app
from flask import Flask, request, jsonify, current_app, g as app_ctx
import requests
from bs4 import BeautifulSoup
import time
import utils

@app.before_request
def logging_before():
  # Store the start time for the request
  app_ctx.start_time = time.perf_counter()
  
    
@app.after_request
def logging_after(response):
  # Get total time in milliseconds
  total_time = time.perf_counter() - app_ctx.start_time
  time_in_ms = int(total_time * 1000)
  # Log the time taken for the endpoint 
  current_app.logger.info('%s ms %s %s %s', time_in_ms, request.method, request.path, dict(request.args))
  return response

@app.route('/')
def index():
    # Home route that returns a string
    return "Mercadolibre Scraper API"

@app.route('/search', methods=['GET'])
def search(): 
    # Get the query parameter from the URL
    query = request.args.get('query', '')
    tld = request.args.get('tld', '')
    page_query = request.args.get('page', '')
    excluded = request.args.getlist('exc[]')
    
    print('excluded', excluded)

    domain = utils.getDomain(tld)
    
    # If no query provided, return an error
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if not page_query:
        page_query = 0
    
    # List to store the scraped products
    page_data = {
       'info': {
          'current_page': int(page_query),
          'url': '',
          'tld': tld
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
      url = f"https://{domain}/{query}{page_suffix}"
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
      title_class = 'ui-search-item__title'
      product_brand_class = "ui-search-item__brand-discoverability ui-search-item__group__element"
      final_price_container_class = "andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript"
      final_price_class = "andes-money-amount__fraction"
      





      
      # Find and iterate over all the product cards
      scraped_products = soup.find_all('li', class_=card_class)
      for card in scraped_products:
        # Find the title, URL, final price, and brand of the product
        is_usd = False
        try:
          prod_link = card.find('a')['href']
        except AttributeError:
           prod_link = ''
        try:
          prod_title = card.find('h2', class_=title_class).text
        except AttributeError:
           prod_title = ''
        try:
          final_price_container = card.find('span', class_=final_price_container_class)
          if 'U$S' in final_price_container.text:
            is_usd = True            
          final_price = int(final_price_container.find('span', class_=final_price_class).text.replace('.', ''))
        except AttributeError:
          final_price = int(card.find('span', class_=final_price_class).text.replace('.', ''))
        try:
            brand_element = card.find('span', class_=product_brand_class)
            brand = brand_element.text.strip() if brand_element and brand_element.text.strip() else None
        except AttributeError:
            brand = None
        
        # Append the product to the list
        page_data['products'].append({
            'title': prod_title,
            'url': prod_link,
            'final_price': final_price,
            'is_usd': is_usd,
            'brand': brand
        })
      
      
      
      print("FINISHED Scraping at ", url)

      
    get_page_data(int(page_query))

    # Remove items that contain excluded words
    def removeExcluded (str):
      if any(exc_word.lower() in str.lower() for exc_word in excluded):
        print(str)
        return False
      return True
      # for exc_word in excluded:
      #     if exc_word != '' and exc_word.lower() in str.lower():
      #       print(exc_word.lower(), str.lower())
      #       return False
      #     return True

    if len(excluded) > 0:
      page_data['products'] = [prod for prod in page_data['products'] if removeExcluded(prod['title'])]


    # Return the list of products as JSON
    if len(page_data['products']) > 0:
      return jsonify(page_data)
    else:
      return jsonify({'error': 'No items found'}), 404
