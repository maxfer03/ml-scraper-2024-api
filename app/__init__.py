from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Importing the routes from the 'app' module
from app import routes