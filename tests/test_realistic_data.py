#!/usr/bin/env python3
"""
Teste com dados realistas simulados do scraper Droga Raia
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.product_unifier import ProductUnifier

def test_with_realistic_data():
    """Teste com dados realistas simulados"""
    print("=== Teste com Dados Realistas Simulados ===")
    print("Buscando: 'dipirona 1g 20 comprimidos'")
    print()
    
    try:
        # Dados realistas simulados do scraper Droga Raia
        print("1. Dados realistas simulados do scraper Droga Raia:")
        realistic_products = [
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
            },
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Medley',
                'description': 'Analgésico e antitérmico',
                'price': 6.90,
                'original_price': 8.50,
                'discount_percentage': 18,
                'product_url': 'https://www.drogaraia.com.br/dipirona-sodica-1g-20-comprimidos-medley',
                'has_discount': True,
                'position': 4
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Cimed',
                'description': 'Analgésico e antitérmico',
                'price': 8.20,
                'original_price': 8.20,
                'discount_percentage': 0,
                'product_url': 'https://www.drogaraia.com.br/dipirona-1g-20-comprimidos-cimed',
                'has_discount': False,
                'position': 5
            }
        ]
        
        # Simular resultados do scraper
        scraper_results = {
            'pharmacy': 'Droga Raia',
            'search_url': 'https://www.drogaraia.com.br/search?q=dipirona+1g+20+comprimidos',
            'products': realistic_products,
            'total_products': len(realistic_products)
        }
        
        # Mostrar produtos ANTES da padronização
        print("2. Produtos encontrados (ANTES do ProductUnifier):")
        for i, product in enumerate(scraper_results['products'], 1):
            print(f"   {i}. Nome: {product['name']}")
            print(f"      Marca: {product['brand']}")
            print(f"      Descrição: {product.get('description', 'N/A')}")
            print(f"      Preço: R$ {product['price']}")
            if product.get('has_discount'):
                print(f"      Desconto: {product.get('discount_percentage', 0)}%")
            print()
        
        # Inicializar ProductUnifier
        print("3. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   ✓ Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        print()
        
        # Processar produtos com ProductUnifier
        print("4. Processando produtos com ProductUnifier...")
        standardized_results = unifier.process_scraper_results(scraper_results)
        
        # Mostrar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        print(f"   Total de produtos: {stats['total_products']}")
        print(f"   Produtos padronizados: {stats['standardized_products']}")
        print(f"   Taxa de padronização: {stats['standardization_rate']:.1f}%")
        print()
        
        # Mostrar produtos DEPOIS da padronização
        print("5. Produtos padronizados (DEPOIS do ProductUnifier):")
        for i, product in enumerate(standardized_results['products'], 1):
            print(f"   {i}. Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score de similaridade: {product['similarity_score']:.2f}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Salvar resultados em JSON
        output_file = "test_results/realistic_data_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'original_results': scraper_results,
                'standardized_results': standardized_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"6. Resultados salvos em: {output_file}")
        print()
        
        # Exemplo de dados para enviar ao backend
        print("7. Exemplo de dados para enviar ao backend:")
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
        
        # Resumo da padronização
        print("8. Resumo da padronização:")
        standardized_count = stats['standardized_products']
        total_count = stats['total_products']
        
        if standardized_count > 0:
            print(f"   ✓ {standardized_count}/{total_count} produtos foram padronizados")
            print(f"   ✓ Taxa de sucesso: {stats['standardization_rate']:.1f}%")
            
            # Mostrar exemplos de padronização
            print("\n   Exemplos de padronização:")
            for product in standardized_results['products'][:3]:
                if product['is_standardized']:
                    print(f"   • '{product['name']}' → '{product['standardized_name']}' (Lab: {product['laboratory']})")
        else:
            print("   ⚠ Nenhum produto foi padronizado")
        
        print("\n=== Teste com dados realistas concluído com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_realistic_data()
    sys.exit(0 if success else 1) 