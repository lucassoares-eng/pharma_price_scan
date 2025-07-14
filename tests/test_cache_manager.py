import unittest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from utils.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    """Testes para o CacheManager"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar diretório temporário para cache
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(cache_dir=self.temp_dir, cache_duration_hours=1)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        # Remover diretório temporário
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_generate_cache_key(self):
        """Testa geração de chaves de cache"""
        # Teste com termos diferentes
        key1 = self.cache_manager._generate_cache_key("paracetamol 500mg")
        key2 = self.cache_manager._generate_cache_key("paracetamol 500mg")
        key3 = self.cache_manager._generate_cache_key("ibuprofeno 400mg")
        
        # Mesmo termo deve gerar mesma chave
        self.assertEqual(key1, key2)
        
        # Termos diferentes devem gerar chaves diferentes
        self.assertNotEqual(key1, key3)
        
        # Teste com normalização
        key4 = self.cache_manager._generate_cache_key("  PARACETAMOL 500MG  ")
        self.assertEqual(key1, key4)
    
    def test_save_and_get_cache(self):
        """Testa salvamento e recuperação de cache"""
        search_term = "paracetamol 500mg"
        test_results = {
            'droga_raia': {
                'pharmacy': 'Droga Raia',
                'products': [{'name': 'Paracetamol', 'price': 5.99}],
                'total_products': 1
            },
            'sao_joao': {
                'pharmacy': 'São João',
                'products': [{'name': 'Paracetamol', 'price': 6.50}],
                'total_products': 1
            }
        }
        
        # Salvar no cache
        self.cache_manager.save_cache_results(search_term, test_results)
        
        # Recuperar do cache
        cached_results = self.cache_manager.get_cached_results(search_term)
        
        # Verificar se os resultados são iguais
        self.assertIsNotNone(cached_results)
        self.assertEqual(cached_results, test_results)
    
    def test_cache_expiration(self):
        """Testa expiração do cache"""
        search_term = "teste expiracao"
        test_results = {'test': 'data'}
        
        # Criar cache manager com duração muito curta
        short_cache_manager = CacheManager(cache_dir=self.temp_dir, cache_duration_hours=0.001)  # ~3.6 segundos
        
        # Salvar no cache
        short_cache_manager.save_cache_results(search_term, test_results)
        
        # Verificar se está disponível imediatamente
        cached_results = short_cache_manager.get_cached_results(search_term)
        self.assertIsNotNone(cached_results)
        
        # Aguardar expiração
        time.sleep(5)
        
        # Verificar se expirou
        cached_results = short_cache_manager.get_cached_results(search_term)
        self.assertIsNone(cached_results)
    
    def test_cache_file_structure(self):
        """Testa estrutura do arquivo de cache"""
        search_term = "teste estrutura"
        test_results = {'test': 'data'}
        
        # Salvar no cache
        self.cache_manager.save_cache_results(search_term, test_results)
        
        # Obter caminho do arquivo
        cache_key = self.cache_manager._generate_cache_key(search_term)
        cache_file_path = self.cache_manager._get_cache_file_path(cache_key)
        
        # Verificar se arquivo existe
        self.assertTrue(os.path.exists(cache_file_path))
        
        # Verificar estrutura do JSON
        with open(cache_file_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Verificar campos obrigatórios
        self.assertIn('search_term', cache_data)
        self.assertIn('timestamp', cache_data)
        self.assertIn('results', cache_data)
        
        # Verificar valores
        self.assertEqual(cache_data['search_term'], search_term)
        self.assertEqual(cache_data['results'], test_results)
        
        # Verificar se timestamp é válido
        timestamp = datetime.fromisoformat(cache_data['timestamp'])
        self.assertIsInstance(timestamp, datetime)
    
    def test_clear_expired_cache(self):
        """Testa limpeza de cache expirado"""
        # Criar cache manager com duração muito curta
        short_cache_manager = CacheManager(cache_dir=self.temp_dir, cache_duration_hours=0.001)
        
        # Salvar alguns caches
        short_cache_manager.save_cache_results("termo1", {'data': '1'})
        short_cache_manager.save_cache_results("termo2", {'data': '2'})
        
        # Aguardar expiração
        time.sleep(5)
        
        # Limpar cache expirado
        short_cache_manager.clear_expired_cache()
        
        # Verificar se arquivos foram removidos
        cache_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.json')]
        self.assertEqual(len(cache_files), 0)
    
    def test_get_cache_stats(self):
        """Testa obtenção de estatísticas do cache"""
        # Salvar alguns caches
        self.cache_manager.save_cache_results("termo1", {'data': '1'})
        self.cache_manager.save_cache_results("termo2", {'data': '2'})
        
        # Obter estatísticas
        stats = self.cache_manager.get_cache_stats()
        
        # Verificar campos obrigatórios
        self.assertIn('total_files', stats)
        self.assertIn('valid_files', stats)
        self.assertIn('expired_files', stats)
        self.assertIn('cache_size_mb', stats)
        
        # Verificar valores
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['valid_files'], 2)
        self.assertEqual(stats['expired_files'], 0)
        self.assertGreater(stats['cache_size_mb'], 0)

if __name__ == '__main__':
    unittest.main() 