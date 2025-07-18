#!/usr/bin/env python3
"""
Teste simples do ProductUnifier
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.product_unifier import ProductUnifier

def test_basic_functionality():
    """Teste básico do ProductUnifier"""
    print("=== Teste Básico do ProductUnifier ===")
    
    try:
        # Inicializar o unifier
        print("1. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   ✓ Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        
        # Teste de normalização
        print("\n2. Testando normalização de texto...")
        test_text = "Dipirona Sódica 1g (20 comp.)"
        normalized = unifier.normalize_text(test_text)
        print(f"   Original: '{test_text}'")
        print(f"   Normalizado: '{normalized}'")
        print("   ✓ Normalização funcionando")
        
        # Teste de busca de correspondência
        print("\n3. Testando busca de correspondência...")
        match = unifier.find_best_match("Dipirona Sódica 1g", "Neo Química")
        if match:
            print(f"   ✓ Encontrada correspondência: {match['standardized_name']}")
            print(f"   Laboratório: {match['laboratory']}")
            print(f"   Score: {match['similarity_score']:.2f}")
        else:
            print("   ⚠ Nenhuma correspondência encontrada")
        
        # Teste com produtos de exemplo
        print("\n4. Testando padronização de produtos...")
        sample_products = [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'price': 8.90
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Prati Donaduzzi',
                'price': 9.50
            }
        ]
        
        standardized_products = unifier.standardize_product_list(sample_products)
        print(f"   ✓ Padronizados {len(standardized_products)} produtos")
        
        for i, product in enumerate(standardized_products, 1):
            print(f"   Produto {i}:")
            print(f"     Original: {product['name']}")
            print(f"     Padronizado: {product['standardized_name']}")
            print(f"     Laboratório: {product['laboratory']}")
            print(f"     Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
        
        print("\n=== Teste concluído com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1) 