from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from scrapers.droga_raia import DrogaRaiaScraper
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Página principal com interface para busca de medicamentos"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_medicines():
    """API endpoint para buscar medicamentos em diferentes farmácias"""
    try:
        data = request.get_json()
        medicine_description = data.get('medicine_description', '').strip()
        
        if not medicine_description:
            return jsonify({'error': 'Descrição do medicamento é obrigatória'}), 400
        
        # Lista de scrapers disponíveis
        scrapers = {
            'droga_raia': DrogaRaiaScraper()
        }
        
        results = {}
        
        # Executar busca em cada farmácia
        for pharmacy_name, scraper in scrapers.items():
            try:
                pharmacy_results = scraper.search(medicine_description)
                results[pharmacy_name] = pharmacy_results
            except Exception as e:
                results[pharmacy_name] = {
                    'error': f'Erro ao buscar em {pharmacy_name}: {str(e)}',
                    'products': []
                }
        
        return jsonify({
            'medicine_description': medicine_description,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 