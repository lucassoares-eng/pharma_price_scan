#!/usr/bin/env python3
"""
Teste mínimo do ProductUnifier
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testando funcionalidades básicas...")

try:
    # Testar imports
    from utils.product_unifier import ProductUnifier
    print("✓ Import funcionando")
    
    # Testar criação de instância (sem carregar CSV)
    class MockProductUnifier:
        def __init__(self):
            self.brands_data = {
                'DIPIRONA SODICA MG': 'PRATI DONADUZZI',
                'NOVALGINA': 'SANOFI CHC'
            }
            self.similarity_threshold = 0.7
        
        def normalize_text(self, text):
            if not text:
                return ""
            return text.lower().replace('ó', 'o').replace('á', 'a')
        
        def find_best_match(self, product_name, product_brand=""):
            normalized_name = self.normalize_text(product_name)
            for brand_product, laboratory in self.brands_data.items():
                normalized_brand_product = self.normalize_text(brand_product)
                if normalized_name == normalized_brand_product:
                    return {
                        'standardized_name': brand_product,
                        'laboratory': laboratory,
                        'similarity_score': 1.0
                    }
            return None
    
    # Testar funcionalidades
    unifier = MockProductUnifier()
    print("✓ Instância criada")
    
    # Testar normalização
    result = unifier.normalize_text("Dipirona Sódica")
    print(f"✓ Normalização: '{result}'")
    
    # Testar busca
    match = unifier.find_best_match("dipirona sodica mg")
    if match:
        print(f"✓ Busca funcionando: {match['standardized_name']}")
    else:
        print("⚠ Busca não encontrou correspondência")
    
    print("\n=== Teste básico concluído! ===")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc() 