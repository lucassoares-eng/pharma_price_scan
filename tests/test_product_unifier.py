import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier, standardize_products
from scrapers.droga_raia import DrogaRaiaScraper

class TestProductUnifier(unittest.TestCase):
    """Testes para o ProductUnifier"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.unifier = ProductUnifier()
        
        # Dados de exemplo do scraper Droga Raia para "dipirona 1g 20 comprimidos"
        self.sample_products = [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico',
                'price': 8.90,
                'original_price': 12.50,
                'discount_percentage': 28,
                'product_url': 'https://www.drogaraia.com.br/dipirona-sodica-1g-20-comprimidos',
                'has_discount': True,
                'position': 1
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Prati Donaduzzi',
                'description': 'Analgésico e antitérmico',
                'price': 9.50,
                'original_price': 9.50,
                'discount_percentage': 0,
                'product_url': 'https://www.drogaraia.com.br/dipirona-1g-20-comprimidos',
                'has_discount': False,
                'position': 2
            },
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'EMS Pharma',
                'description': 'Analgésico e antitérmico',
                'price': 7.80,
                'original_price': 10.00,
                'discount_percentage': 22,
                'product_url': 'https://www.drogaraia.com.br/dipirona-sodica-1g-20-comprimidos-ems',
                'has_discount': True,
                'position': 3
            }
        ]
    
    def test_load_brands_data(self):
        """Testa se os dados de marcas são carregados corretamente"""
        self.assertIsInstance(self.unifier.brands_data, dict)
        self.assertGreater(len(self.unifier.brands_data), 0)
        
        # Verificar se alguns produtos conhecidos estão presentes
        self.assertIn('DIPIRONA SODICA MG', self.unifier.brands_data)
        self.assertIn('NOVALGINA', self.unifier.brands_data)
    
    def test_normalize_text(self):
        """Testa a normalização de texto"""
        # Teste com acentos
        self.assertEqual(self.unifier.normalize_text('Dipirona Sódica'), 'dipirona sodica')
        
        # Teste com caracteres especiais
        self.assertEqual(self.unifier.normalize_text('Dipirona 1g (20 comp.)'), 'dipirona 1g 20 comp')
        
        # Teste com texto vazio
        self.assertEqual(self.unifier.normalize_text(''), '')
        self.assertEqual(self.unifier.normalize_text(None), '')
    
    def test_find_best_match(self):
        """Testa a busca de correspondência na lista de marcas"""
        # Teste com produto que existe na lista
        match = self.unifier.find_best_match('Dipirona Sódica 1g', 'Neo Química')
        self.assertIsNotNone(match)
        self.assertIn('standardized_name', match)
        self.assertIn('laboratory', match)
        self.assertIn('similarity_score', match)
        
        # Teste com produto que não existe na lista
        match = self.unifier.find_best_match('Produto Inexistente', 'Marca Inexistente')
        self.assertIsNone(match)
    
    def test_standardize_product_list(self):
        """Testa a padronização de uma lista de produtos"""
        standardized_products = self.unifier.standardize_product_list(self.sample_products)
        
        self.assertEqual(len(standardized_products), len(self.sample_products))
        
        for product in standardized_products:
            # Verificar se os campos de padronização foram adicionados
            self.assertIn('standardized_name', product)
            self.assertIn('laboratory', product)
            self.assertIn('similarity_score', product)
            self.assertIn('is_standardized', product)
            
            # Verificar se os dados originais foram preservados
            self.assertIn('name', product)
            self.assertIn('brand', product)
            self.assertIn('price', product)
    
    def test_process_scraper_results(self):
        """Testa o processamento de resultados de scraper"""
        scraper_results = {
            'pharmacy': 'Droga Raia',
            'search_url': 'https://www.drogaraia.com.br/search?q=dipirona+1g+20+comprimidos',
            'products': self.sample_products,
            'total_products': len(self.sample_products)
        }
        
        standardized_results = self.unifier.process_scraper_results(scraper_results)
        
        # Verificar se os resultados foram padronizados
        self.assertIn('products', standardized_results)
        self.assertIn('standardization_stats', standardized_results)
        
        # Verificar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        self.assertIn('total_products', stats)
        self.assertIn('standardized_products', stats)
        self.assertIn('standardization_rate', stats)
        
        self.assertEqual(stats['total_products'], len(self.sample_products))
    
    def test_standardize_products_function(self):
        """Testa a função de conveniência standardize_products"""
        standardized_products = standardize_products(self.sample_products)
        
        self.assertEqual(len(standardized_products), len(self.sample_products))
        
        for product in standardized_products:
            self.assertIn('standardized_name', product)
            self.assertIn('laboratory', product)
            self.assertIn('similarity_score', product)
            self.assertIn('is_standardized', product)

class TestProductUnifierWithRealScraper(unittest.TestCase):
    """Testes integrados com o scraper real"""
    
    @patch('scrapers.droga_raia.DrogaRaiaScraper.make_request')
    @patch('scrapers.droga_raia.DrogaRaiaScraper.parse_html')
    def test_integration_with_droga_raia_scraper(self, mock_parse_html, mock_make_request):
        """Testa integração com o scraper Droga Raia"""
        # Mock da resposta do scraper
        mock_response = {
            'content': '<html>...</html>',
            'status_code': 200
        }
        mock_make_request.return_value = mock_response
        
        # Mock do HTML parseado
        mock_soup = MagicMock()
        mock_parse_html.return_value = mock_soup
        
        # Configurar o mock para retornar produtos de exemplo
        # (simulação do que o scraper retornaria)
        sample_products = [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico',
                'price': 8.90,
                'original_price': 12.50,
                'discount_percentage': 28,
                'product_url': 'https://www.drogaraia.com.br/dipirona-sodica-1g-20-comprimidos',
                'has_discount': True,
                'position': 1
            }
        ]
        
        # Simular o comportamento do scraper
        scraper = DrogaRaiaScraper()
        scraper_results = {
            'pharmacy': 'Droga Raia',
            'search_url': 'https://www.drogaraia.com.br/search?q=dipirona+1g+20+comprimidos',
            'products': sample_products,
            'total_products': len(sample_products)
        }
        
        # Processar com o ProductUnifier
        unifier = ProductUnifier()
        standardized_results = unifier.process_scraper_results(scraper_results)
        
        # Verificar se a padronização funcionou
        self.assertIn('products', standardized_results)
        self.assertIn('standardization_stats', standardized_results)
        
        # Verificar se pelo menos um produto foi processado
        self.assertGreater(len(standardized_results['products']), 0)
        
        # Verificar se o produto tem os campos de padronização
        product = standardized_results['products'][0]
        self.assertIn('standardized_name', product)
        self.assertIn('laboratory', product)
        self.assertIn('similarity_score', product)
        self.assertIn('is_standardized', product)

if __name__ == '__main__':
    unittest.main() 