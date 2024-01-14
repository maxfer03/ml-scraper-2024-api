import awsgi
from flask import Flask
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
# Importing the routes from the 'app' module
from app import routes

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})