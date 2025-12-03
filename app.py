"""Flask web application for the search engine."""

import os
import time
from flask import Flask, jsonify, render_template, request

from src.indexer import Indexer
from src.search_engine import SearchEngine

app = Flask(__name__)

# Initialize the indexer and search engine
indexer = Indexer()
search_engine = None

# Try to load existing index
index_path = os.path.join(os.path.dirname(__file__), 'data', 'inverted_index.pkl')
if os.path.exists(index_path):
    indexer.load_index(index_path)
    search_engine = SearchEngine(indexer)


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/search')
def search():
    """Handle search queries and return results."""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('index.html')
    
    start_time = time.time()
    
    results = []
    if search_engine:
        results = search_engine.search(query, top_k=10)
    
    elapsed_time = round(time.time() - start_time, 4)
    
    return render_template('results.html', 
                         query=query, 
                         results=results, 
                         time=elapsed_time)


@app.route('/api/search')
def api_search():
    """API endpoint for search queries."""
    query = request.args.get('q', '').strip()
    top_k = request.args.get('top_k', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter q is required'}), 400
    
    start_time = time.time()
    
    results = []
    if search_engine:
        results = search_engine.search(query, top_k=top_k)
    
    elapsed_time = round(time.time() - start_time, 4)
    
    return jsonify({
        'query': query,
        'results': results,
        'time': elapsed_time,
        'count': len(results)
    })


if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable for development
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
