#!/usr/bin/env python3
"""
Demonstração do ProductUnifier com dados simulados
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.product_unifier import ProductUnifier

def demo_product_unifier():
    """Demonstra o funcionamento do ProductUnifier"""
    print("=== Demonstração do ProductUnifier ===")
    print("Buscando: 'dipirona 1g 20 comprimidos'")
    print()
    
    try:
        # Inicializar ProductUnifier
        print("1. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   ✓ Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        print()
        
        # Dados simulados do scraper Droga Raia
        print("2. Dados simulados do scraper Droga Raia:")
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
        
        for i, product in enumerate(sample_products, 1):
            print(f"   {i}. {product['name']} - {product['brand']}")
            print(f"      Preço: R$ {product['price']}")
        print()
        
        # Simular resultados do scraper
        scraper_results = {
            'pharmacy': 'Droga Raia',
            'search_url': 'https://www.drogaraia.com.br/search?q=dipirona+1g+20+comprimidos',
            'products': sample_products,
            'total_products': len(sample_products)
        }
        
        # Processar com ProductUnifier
        print("3. Processando produtos com ProductUnifier...")
        standardized_results = unifier.process_scraper_results(scraper_results)
        
        # Mostrar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        print(f"   Total de produtos: {stats['total_products']}")
        print(f"   Produtos padronizados: {stats['standardized_products']}")
        print(f"   Taxa de padronização: {stats['standardization_rate']:.1f}%")
        print()
        
        # Mostrar produtos padronizados
        print("4. Produtos padronizados:")
        for i, product in enumerate(standardized_results['products'], 1):
            print(f"   {i}. Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score de similaridade: {product['similarity_score']:.2f}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Exemplo de dados para enviar ao backend
        print("5. Exemplo de dados para enviar ao backend:")
        backend_data = {
            'search_query': 'dipirona 1g 20 comprimidos',
            'pharmacy': standardized_results['pharmacy'],
            'standardized_products': [
                {
                    'standardized_name': p['standardized_name'],
                    'laboratory': p['laboratory'],
                    'original_name': p['name'],
                    'original_brand': p['brand'],
                    'price': p['price'],
                    'similarity_score': p['similarity_score'],
                    'is_standardized': p['is_standardized']
                }
                for p in standardized_results['products']
            ],
            'standardization_stats': standardized_results['standardization_stats']
        }
        
        print(json.dumps(backend_data, indent=2, ensure_ascii=False))
        print()
        
        # Salvar resultados em JSON
        output_file = "test_results/demo_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_results, f, indent=2, ensure_ascii=False)
        
        print(f"6. Resultados salvos em: {output_file}")
        print()
        
        print("=== Demonstração concluída com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_product_unifier()
    sys.exit(0 if success else 1) 