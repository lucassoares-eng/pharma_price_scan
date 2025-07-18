#!/usr/bin/env python3
"""
Teste da nova lógica do ProductUnifier
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def test_new_logic():
    """Teste da nova lógica do ProductUnifier"""
    print("=== Teste da Nova Lógica do ProductUnifier ===")
    print("Testando: busca por laboratório na descrição primeiro")
    print()
    
    try:
        # Inicializar ProductUnifier
        print("1. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   ✓ Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        print()
        
        # Dados de teste com diferentes cenários
        test_products = [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico fabricado pela NEO QUIMICA',
                'price': 8.90
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Prati Donaduzzi',
                'description': 'Analgésico e antitérmico da PRATI DONADUZZI',
                'price': 9.50
            },
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'EMS Pharma',
                'description': 'Analgésico e antitérmico - EMS PHARMA',
                'price': 7.80
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Cimed',
                'description': 'Analgésico e antitérmico fabricado pela CIMED',
                'price': 8.20
            },
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Medley',
                'description': 'Analgésico e antitérmico da MEDLEY',
                'price': 6.90
            }
        ]
        
        # Simular resultados do scraper
        scraper_results = {
            'pharmacy': 'Droga Raia',
            'search_url': 'https://www.drogaraia.com.br/search?q=dipirona+1g+20+comprimidos',
            'products': test_products,
            'total_products': len(test_products)
        }
        
        # Mostrar produtos ANTES da padronização
        print("2. Produtos encontrados (ANTES do ProductUnifier):")
        for i, product in enumerate(scraper_results['products'], 1):
            print(f"   {i}. Nome: {product['name']}")
            print(f"      Marca: {product['brand']}")
            print(f"      Descrição: {product.get('description', 'N/A')}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Processar produtos com ProductUnifier
        print("3. Processando produtos com nova lógica...")
        standardized_results = unifier.process_scraper_results(scraper_results)
        
        # Mostrar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        print(f"   Total de produtos: {stats['total_products']}")
        print(f"   Produtos padronizados: {stats['standardized_products']}")
        print(f"   Taxa de padronização: {stats['standardization_rate']:.1f}%")
        print()
        
        # Mostrar produtos DEPOIS da padronização
        print("4. Produtos padronizados (DEPOIS do ProductUnifier):")
        for i, product in enumerate(standardized_results['products'], 1):
            print(f"   {i}. Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score de similaridade: {product['similarity_score']:.2f}")
            print(f"      Tipo de correspondência: {product.get('match_type', 'N/A')}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Análise dos tipos de correspondência
        print("5. Análise dos tipos de correspondência:")
        match_types = {}
        for product in standardized_results['products']:
            match_type = product.get('match_type', 'unknown')
            if match_type not in match_types:
                match_types[match_type] = 0
            match_types[match_type] += 1
        
        for match_type, count in match_types.items():
            print(f"   • {match_type}: {count} produtos")
        print()
        
        # Salvar resultados em JSON
        output_file = "test_results/new_logic_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_results, f, indent=2, ensure_ascii=False)
        
        print(f"6. Resultados salvos em: {output_file}")
        print()
        
        print("=== Teste da nova lógica concluído com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_logic()
    sys.exit(0 if success else 1) 