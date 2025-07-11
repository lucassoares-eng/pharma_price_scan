#!/usr/bin/env python3
"""
Teste do DrogaRaiaScraper para o produto ibuprofeno 600mg comprimido
"""
import logging
from scrapers.droga_raia import DrogaRaiaScraper

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    print("Testando busca real no Droga Raia com Selenium para: ibuprofeno 600mg comprimido\n")
    
    scraper = DrogaRaiaScraper()
    result = scraper.search("ibuprofeno 600mg comprimido")
    
    print("\n==== RESULTADO FINAL ====")
    print(f"Farmácia: {result.get('pharmacy')}")
    print(f"URL: {result.get('url')}")
    print(f"Total de produtos: {result.get('total_products')}")
    
    if 'error' in result:
        print(f"Erro: {result['error']}")
    else:
        print(f"\nProdutos encontrados ({len(result.get('products', []))}):")
        for i, prod in enumerate(result.get('products', []), 1):
            print(f"\n--- Produto {i} ---")
            print(f"Nome: {prod.get('name', 'N/A')}")
            print(f"Marca: {prod.get('brand', 'N/A')}")
            print(f"Descrição: {prod.get('description', 'N/A')}")
            print(f"Preço atual: {prod.get('price', 'N/A')}")
            print(f"Preço original: {prod.get('original_price', 'N/A')}")
            if prod.get('has_discount', False):
                print(f"Desconto: {prod.get('discount_percentage', 0)}%")
            print(f"URL do produto: {prod.get('product_url', 'N/A')}")
            print(f"URL da imagem: {prod.get('image_url', 'N/A')}")

if __name__ == "__main__":
    main() 