#!/usr/bin/env python3
"""
Teste do unificador com dados melhorados do scraper São João
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def test_unifier_with_improved_data():
    """Testa o unificador com dados melhorados"""
    
    # Dados de exemplo com marcas corretas extraídas
    test_data = {
        "droga_raia": {
            "pharmacy": "Droga Raia",
            "products": [
                {
                    "brand": "Buprovil",
                    "description": "20 Comprimidos",
                    "discount_percentage": 18,
                    "has_discount": True,
                    "name": "Buprovil Ibuprofeno 600mg 20 comprimidos",
                    "original_price": 26.14,
                    "position": 4,
                    "price": 21.39,
                    "product_url": "https://www.drogaraia.com.br/buprovil-600mg-20-comprimidos.html?origin=search"
                },
                {
                    "brand": "Algy-Flanderil",
                    "description": "20 Comprimidos",
                    "discount_percentage": 8,
                    "has_discount": True,
                    "name": "Algy-Flanderil Ibuprofeno 600mg 20 comprimidos",
                    "original_price": 25.22,
                    "position": 3,
                    "price": 23.32,
                    "product_url": "https://www.drogaraia.com.br/algy-flanderil-600mg-com-20-comprimidos.html?origin=search"
                },
                {
                    "brand": "Prati Donaduzzi",
                    "description": "20 Comprimidos Revestidos",
                    "discount_percentage": 0,
                    "has_discount": False,
                    "name": "Ibuprofeno 600mg 20 comprimidos Farmaco Prati Genérico",
                    "original_price": 23.7,
                    "position": 1,
                    "price": 23.7,
                    "product_url": "https://www.drogaraia.com.br/ibuprofeno-600mg-farmaco-generico-com-20-comprimidos-revestidos.html?origin=search"
                },
                {
                    "brand": "Ibupril",
                    "description": "20 Comprimidos Revestidos",
                    "discount_percentage": 6,
                    "has_discount": True,
                    "name": "Ibupril Ibuprofeno 600mg 20 comprimidos",
                    "original_price": 25.46,
                    "position": 2,
                    "price": 23.99,
                    "product_url": "https://www.drogaraia.com.br/ibupril-600-mg-20-comprimidos.html?origin=search"
                }
            ],
            "total_products": 4,
            "url": "https://www.drogaraia.com.br/search?w=ibuprofeno+600mg+20+comprimidos"
        },
        "sao_joao": {
            "pharmacy": "São João",
            "products": [
                {
                    "brand": "Prati Donaduzzi",
                    "description": "600mg 20 Comprimidos",
                    "discount_percentage": 35,
                    "has_discount": True,
                    "name": "Ibuprofeno Genérico Prati-Donaduzzi 600mg 20 Comprimidos Revestidos",
                    "original_price": 22.99,
                    "position": 2,
                    "price": 14.9,
                    "product_url": "https://www.saojoaofarmacias.com.br/ibuprofeno-generico-prati-donaduzzi-600mg-20-comprimidos-revestidos-10099287/p"
                },
                {
                    "brand": "Vitamedic",
                    "description": "600mg 20 Comprimidos",
                    "discount_percentage": 0,
                    "has_discount": False,
                    "name": "Ibuprofeno 600mg 20 Comprimidos",
                    "original_price": 18.9,
                    "position": 1,
                    "price": 18.9,
                    "product_url": "https://www.saojoaofarmacias.com.br/ibuprofeno-600mg-20-comprimidos-13308/p"
                }
            ],
            "total_products": 2,
            "url": "https://www.saojoaofarmacias.com.br/ibuprofeno%20600mg%2020%20comprimidos?_q=ibuprofeno%20600mg%2020%20comprimidos&map=ft"
        }
    }
    
    # Criar instância do unificador
    unifier = ProductUnifier(similarity_threshold=0.7)
    
    print("=== Teste do Unificador com Dados Melhorados ===\n")
    
    # Testar unificação
    print("1. Testando unificação de produtos...")
    unified_results = unifier.unify_products(test_data)
    
    print(f"   Produtos originais: {sum(len(pharmacy['products']) for pharmacy in test_data.values() if 'products' in pharmacy)}")
    print(f"   Produtos unificados: {len(unified_results.get('unified_products', []))}")
    
    # Mostrar resultados unificados
    print("\n2. Produtos unificados encontrados:")
    for i, product in enumerate(unified_results.get('unified_products', []), 1):
        print(f"\n   Produto {i}:")
        print(f"     Nome: {product['unified_name']}")
        print(f"     Marca: {product['unified_brand']}")
        print(f"     Melhor preço: R$ {product['best_price']:.2f} em {product['best_price_pharmacy']}")
        print(f"     Variações: {product['total_variants']}")
        
        if product['total_variants'] > 1:
            print("     Variações encontradas:")
            for variant in product['variants']:
                print(f"       - {variant['name']} (R$ {variant['price']:.2f} em {variant['pharmacy']})")
    
    # Testar similaridade entre produtos específicos
    print("\n3. Testando similaridade entre produtos específicos...")
    
    # Produtos que deveriam ser similares (Prati Donaduzzi)
    product1 = test_data['droga_raia']['products'][2]  # Prati Donaduzzi da Raia
    product2 = test_data['sao_joao']['products'][0]    # Prati Donaduzzi da São João
    
    similarity = unifier.calculate_similarity(product1, product2)
    print(f"   Similaridade entre produtos Prati Donaduzzi: {similarity:.3f}")
    
    # Produtos que não deveriam ser similares
    product3 = test_data['droga_raia']['products'][0]  # Buprovil
    product4 = test_data['sao_joao']['products'][1]    # Vitamedic
    
    similarity2 = unifier.calculate_similarity(product3, product4)
    print(f"   Similaridade entre produtos diferentes: {similarity2:.3f}")
    
    # Salvar resultados em arquivo JSON para inspeção
    with open('test_unifier_improved_results.json', 'w', encoding='utf-8') as f:
        json.dump(unified_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n4. Resultados salvos em 'test_unifier_improved_results.json'")
    
    return unified_results

if __name__ == "__main__":
    test_unifier_with_improved_data() 