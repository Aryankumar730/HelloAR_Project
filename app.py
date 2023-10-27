from flask import Flask, jsonify, request, redirect
import string
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)


class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(10), unique=True, nullable=False)
    long_url = db.Column(db.String(200), nullable=False)
    total_hits = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<URL: {self.short_url}>'
    
    
# FUNCTION TO GENERATE THE RANDOM STRING FOR SHORT URL
# MAXIMUM COMBINATIONS ARE USING (A-Z) , (a-z), (0 -9) ARE 62 RAISE TO POWER 8.

def generate_short_url():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(8))



# ENDPOINT FOR MAKING SHORT URL

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    long_url = request.json.get('long_url')
    if not long_url:
        return jsonify({'error': 'Missing long_url parameter'}), 400

    short_url = generate_short_url()
    # url_mapping[f'http://HelloAR/{short_url}'] = long_url
    new_mapping = URLMapping(short_url=short_url, long_url=long_url)
    db.session.add(new_mapping)
    db.session.commit()

    return jsonify({'short_url': f"https://{request.host}/{short_url}"}), 200



# ENDPOINT FOR GETTING LONG URL

@app.route('/<short_url>', methods=['GET'])
def get_long_url(short_url):
    mapping = URLMapping.query.filter_by(short_url=short_url).first()

    if mapping:
        mapping.total_hits += 1
        db.session.commit()
        long_url = mapping.long_url
        return jsonify({'long_url': f"{long_url}"}), 200
    else:
        return jsonify({'error': 'Short URL not found'}), 404
    

# ENDPOINT FOR SEARCH
    

@app.route('/search', methods=['GET'])
def search_urls():
    search_term = request.args.get('term')
    if not search_term:
        return jsonify({'error': 'Missing search term'}), 400

    results = URLMapping.query.filter(URLMapping.long_url.like(f'%{search_term}%')).all()
    print(results)
    if results:
        return jsonify({'results': [{'short_url': result.short_url, 'long_url': result.long_url} for result in results]}), 200
    else:
        return jsonify({'message': 'No results found'}), 404
    

# ENDPOINT FOR METADATA

@app.route('/metadata/<short_url>', methods=['GET'])
def get_url_metadata(short_url):
    mapping = URLMapping.query.filter_by(short_url=short_url).first()
    if mapping:
        return jsonify({'short_url': mapping.short_url, 'long_url': mapping.long_url, 'total_hits': mapping.total_hits}), 200
    else:
        return jsonify({'error': 'Short URL not found'}), 404
    

if __name__ == '__main__':
    app.run(debug=True)
