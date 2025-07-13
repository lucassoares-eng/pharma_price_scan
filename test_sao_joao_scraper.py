#!/usr/bin/env python3
"""
Teste do scraper São João
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.sao_joao import SaoJoaoScraper
import json

def test_sao_joao_scraper():
    """Testa o scraper São João com um medicamento específico"""
    
    print("Iniciando teste do scraper São João...")
    
    try:
        # Criar instância do scraper
        scraper = SaoJoaoScraper()
        
        # Testar busca
        medicine = "ibuprofeno 600mg 20"
        print(f"Buscando: {medicine}")
        
        result = scraper.search(medicine)
        
        # Salvar HTML para análise
        if hasattr(scraper, 'driver') and scraper.driver:
            with open('sao_joao_debug.html', 'w', encoding='utf-8') as f:
                f.write(scraper.driver.page_source)
            print("HTML da página salvo em: sao_joao_debug.html")
        
        # Exibir resultados
        print(f"\nResultados da busca:")
        print(f"Farmácia: {result.get('pharmacy', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        print(f"Total de produtos: {result.get('total_products', 0)}")
        
        if result.get('error'):
            print(f"Erro: {result['error']}")
        else:
            print(f"\nProdutos encontrados:")
            for i, product in enumerate(result.get('products', []), 1):
                print(f"\n{i}. {product.get('name', 'N/A')}")
                print(f"   Marca: {product.get('brand', 'N/A')}")
                print(f"   Preço: R$ {product.get('price', 'N/A')}")
                print(f"   Preço original: R$ {product.get('original_price', 'N/A')}")
                print(f"   Desconto: {product.get('discount_percentage', 0)}%")
                print(f"   URL: {product.get('product_url', 'N/A')}")
        
        # Salvar resultado em JSON para análise
        with open('sao_joao_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResultado salvo em: sao_joao_test_result.json")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpar recursos
        if 'scraper' in locals():
            scraper.cleanup()

if __name__ == "__main__":
    test_sao_joao_scraper() 