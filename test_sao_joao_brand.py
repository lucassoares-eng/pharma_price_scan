#!/usr/bin/env python3
"""
Teste para verificar se a extração de marca do scraper São João está funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.sao_joao import SaoJoaoScraper

def test_sao_joao_brand_extraction():
    """Testa se a extração de marca está funcionando corretamente"""
    
    print("🧪 Testando extração de marca do scraper São João...")
    print()
    
    # Criar instância do scraper
    scraper = SaoJoaoScraper()
    
    # Testar busca de medicamento
    search_term = "losartana 50mg 30 comprimidos"
    print(f"🔍 Buscando: {search_term}")
    print()
    
    try:
        # Fazer busca
        results = scraper.search(search_term)
        
        if 'error' in results:
            print(f"❌ Erro na busca: {results['error']}")
            return
        
        print(f"📊 Resultados encontrados:")
        print(f"   - Total de produtos: {len(results.get('products', []))}")
        print()
        
        # Analisar produtos
        products = results.get('products', [])
        products_with_brand = []
        products_without_brand = []
        
        for i, product in enumerate(products[:5], 1):  # Analisar apenas os 5 primeiros
            brand = product.get('brand', '')
            name = product.get('name', 'N/A')
            
            print(f"   {i}. {name}")
            print(f"      Marca: '{brand}'")
            print(f"      Preço: R$ {product.get('price', 'N/A')}")
            print()
            
            if brand and brand != "Marca não disponível" and brand.strip():
                products_with_brand.append(product)
            else:
                products_without_brand.append(product)
        
        print(f"📈 Estatísticas:")
        print(f"   - Produtos com marca: {len(products_with_brand)}")
        print(f"   - Produtos sem marca: {len(products_without_brand)}")
        print(f"   - Taxa de sucesso: {len(products_with_brand) / len(products) * 100:.1f}%")
        
        if len(products_without_brand) > 0:
            print()
            print("⚠️  Produtos sem marca identificada:")
            for product in products_without_brand:
                print(f"      - {product.get('name', 'N/A')}")
        
        print()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sao_joao_brand_extraction() 