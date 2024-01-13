from app import app

@app.route('/')
def index():
    return "Mercadolibre Scraper API"
