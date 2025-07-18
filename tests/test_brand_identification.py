#!/usr/bin/env python3
"""
Teste específico para verificar a identificação de marca baseada na primeira palavra
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def test_brand_identification():
    """Teste específico para identificação de marca"""
    print("=== Teste de Identificação de Marca Baseada na Primeira Palavra ===")
    
    try:
        # Inicializar ProductUnifier
        unifier = ProductUnifier()
        
        # Dados reais do cache (exemplo fornecido)
        test_products = [
            {
                'name': 'Dipirona Monoidratada 1g 20 comprimidos Prati Donaduzzi Genérico',
                'brand': 'Dipirona Sodica',
                'description': '20 Comprimidos',
                'price': 19.98
            },
            {
                'name': 'Atroveran Dip Dipirona Monoidratada 1g 20 comprimidos',
                'brand': 'Atroveran',
                'description': '20 Comprimidos',
                'price': 21.99
            },
            {
                'name': 'Maxalgina Dipirona Monoidratada 1g 20 Comprimidos',
                'brand': 'Maxalgina',
                'description': '20 Comprimidos',
                'price': 22.67
            },
            {
                'name': 'Anador 1G 20 comprimidos',
                'brand': 'Anador',
                'description': '20 Comprimidos',
                'price': 26.49
            },
            {
                'name': 'Dipirona Monoidratada 1g 20 Comprimidos Neo Química Genérico',
                'brand': 'Dipirona Sodica',
                'description': '20 Comprimidos',
                'price': 26.85
            }
        ]
        
        search_term = "dipirona 1g 20 comprimidos"
        
        print(f"Termo de busca: '{search_term}'")
        print()
        
        print("1. Testando identificação de marca para cada produto:")
        for i, product in enumerate(test_products, 1):
            print(f"\n   Produto {i}:")
            print(f"      Nome: {product['name']}")
            print(f"      Marca original: {product['brand']}")
            
            # Testar identificação de marca
            identified_brand = unifier.identify_brand_from_name(product['name'], search_term)
            print(f"      Marca identificada: {identified_brand}")
            
            # Testar find_best_match completo
            match = unifier.find_best_match(
                product['name'],
                product['brand'],
                product['description'],
                search_term
            )
            
            if match:
                print(f"      Nome padronizado: {match['standardized_name']}")
                print(f"      Laboratório: {match['laboratory']}")
                print(f"      Score: {match['similarity_score']:.2f}")
                print(f"      Tipo: {match.get('match_type', 'unknown')}")
            else:
                print(f"      ✗ Nenhuma correspondência encontrada")
        
        print("\n2. Processando lista completa de produtos:")
        
        # Adicionar search_term aos produtos
        for product in test_products:
            product['search_term'] = search_term
        
        # Processar com ProductUnifier
        standardized_products = unifier.standardize_product_list(test_products)
        
        print(f"   Total de produtos: {len(standardized_products)}")
        standardized_count = sum(1 for p in standardized_products if p.get('is_standardized', False))
        print(f"   Produtos padronizados: {standardized_count}")
        print(f"   Taxa de padronização: {(standardized_count / len(standardized_products) * 100):.1f}%")
        
        print("\n3. Resultados detalhados:")
        for i, product in enumerate(standardized_products, 1):
            print(f"\n   Produto {i}:")
            print(f"      Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score: {product['similarity_score']:.2f}")
            print(f"      Tipo: {product.get('match_type', 'unknown')}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
        
        # Salvar resultados
        output_file = "test_results/brand_identification_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'search_term': search_term,
                'original_products': test_products,
                'standardized_products': standardized_products
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n4. Resultados salvos em: {output_file}")
        
        print("\n=== Teste de identificação de marca concluído! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_brand_identification()
    sys.exit(0 if success else 1) 