import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import utilities
from utils.vector_db import FAISSVectorStore
from utils.groq_generator import GroqGenerator

app = Flask(__name__)

# Initialize database and generator
try:
    vector_store = FAISSVectorStore()
    groq_generator = GroqGenerator()
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    vector_store = None
    groq_generator = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not vector_store or not groq_generator:
        return jsonify({
            'success': False,
            'error': 'Server initialization failed. Check server logs.'
        }), 500

    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    content_type = data.get('content_type', data.get('platform', 'Blog Post')).strip()
    tone = data.get('tone', 'Professional').strip()
    keywords = data.get('keywords', '').strip()

    if not topic:
        return jsonify({
            'success': False,
            'error': 'Topic is required.'
        }), 400

    try:
        # 1. Similarity search using the topic to find RAG context
        search_query = f"Topic: {topic}. Content Type: {content_type}."
        retrieved_context = vector_store.search_similar(search_query, top_k=2)
        
        # Prepare context metadata for client display
        rag_sources = []
        for item in retrieved_context:
            rag_sources.append({
                'topic': item['topic'],
                'content_type': item['content_type'],
                'tone': item['tone'],
                'timestamp': item['timestamp']
            })

        # 2. Generate content using Groq LLM
        generated_content = groq_generator.generate_content(
            topic=topic,
            content_type=content_type,
            tone=tone,
            keywords=keywords,
            retrieved_context=retrieved_context
        )

        # Check for error message
        if generated_content.startswith("Error"):
            return jsonify({
                'success': False,
                'error': generated_content
            }), 400

        # 3. Add generated content to FAISS vector store & Pickle file
        vector_store.add_content(
            topic=topic,
            content_type=content_type,
            tone=tone,
            generated_content=generated_content,
            keywords=keywords
        )

        return jsonify({
            'success': True,
            'content': generated_content,
            'rag_sources': rag_sources
        })

    except Exception as e:
        logger.exception("Failed to generate content")
        return jsonify({
            'success': False,
            'error': f"An internal server error occurred: {str(e)}"
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    if not vector_store:
        return jsonify([])
    try:
        history = vector_store.get_all_history()
        return jsonify(history)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    if not vector_store:
        return jsonify({'success': False, 'error': 'Database not initialized'}), 500
    try:
        vector_store.clear_history()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)