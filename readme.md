# MercadoLibre Scraper API
This is an Open Source API allows to scrape the MercadoLibre site for specific products given a query.

I'm currently hosting the API on AWS with lambda and APIGateway [here](https://ikx2v8qnc6.execute-api.us-east-1.amazonaws.com/dev/).

I'm also working on a [front-end client](https://github.com/maxfer03/ml-scraper-2024-client), you can vist it live [here](https://meliscraper.vercel.app/).

## Endpoints
### `/`
Home endpoint. Nothing much right now
### `/search`
You can do your searches here. Accepts two queries:
- `query`: the specific product you are looking for
- `page`: go to a specific page from that product's listings.

## Setup
- Initiate repo's virtual env
- Install dependencies with the `requirements.txt`
- run `flask run --debug`