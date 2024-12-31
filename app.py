# Import required libraries
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the URL mapping model
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

# Helper function to generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(characters, k=6))  # Generate a 6-character short URL
        if not URLMapping.query.filter_by(short_url=short_url).first():
            return short_url

# Route to serve the home page
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the URL Shortener Service! Use the /shorten endpoint to create short URLs."})

# Route to handle favicon.ico requests
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Route to shorten a URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('original_url')

    if not original_url:
        return jsonify({'error': 'Original URL is required'}), 400

    # Check if the URL has already been shortened
    existing_mapping = URLMapping.query.filter_by(original_url=original_url).first()
    if existing_mapping:
        return jsonify({'short_url': request.host_url + existing_mapping.short_url}), 200

    # Generate a new short URL
    short_url = generate_short_url()

    # Save the mapping in the database
    new_mapping = URLMapping(original_url=original_url, short_url=short_url)
    db.session.add(new_mapping)
    db.session.commit()

    return jsonify({'short_url': request.host_url + short_url}), 201

# Route to handle redirection
@app.route('/<short_url>', methods=['GET'])
def redirect_to_original(short_url):
    mapping = URLMapping.query.filter_by(short_url=short_url).first()

    if mapping:
        return redirect(mapping.original_url)

    return jsonify({'error': 'Short URL not found'}), 404

# Route to list all URL mappings (for debugging/testing purposes)
@app.route('/urls', methods=['GET'])
def list_urls():
    mappings = URLMapping.query.all()
    return jsonify([
        {'original_url': mapping.original_url, 'short_url': request.host_url + mapping.short_url}
        for mapping in mappings
    ])

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run(debug=True)
