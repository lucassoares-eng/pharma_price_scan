#!/usr/bin/env python3
"""
Teste do scraper SaoJoaoScraper com busca por 'ibuprofone 600mg 20 comprimidos'
"""
import sys
import os
import json
from scrapers.sao_joao import SaoJoaoScraper
from utils.product_unifier import ProductUnifier

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("=== Teste: SaoJoaoScraper + ProductUnifier ===")
    search_term = "ibuprofone 600mg 20 comprimidos"
    print(f"Buscando: {search_term}\n")
    
    # Inicializar scraper e driver (assume que Selenium está configurado)
    scraper = SaoJoaoScraper()
    results = scraper.search(search_term)
    
    print(f"Produtos encontrados: {len(results.get('products', []))}")
    for i, product in enumerate(results.get('products', [])):
        print(f"\nProduto {i+1}:")
        print(f"  Nome: {product.get('name')}")
        print(f"  Marca extraída: {product.get('brand')}")
        print(f"  Descrição: {product.get('description')}")
        print(f"  URL: {product.get('product_url')}")
        print(f"  Preço: {product.get('price')}")
        print(f"  Tem desconto: {product.get('has_discount')}")
    
    # Testar ProductUnifier diretamente
    unifier = ProductUnifier()
    print("\n=== Testando ProductUnifier diretamente ===")
    for i, product in enumerate(results.get('products', [])):
        match = unifier.find_best_match(
            product_name=product.get('name', ''),
            product_brand=product.get('brand', ''),
            product_description=product.get('description', ''),
            search_term=search_term
        )
        print(f"\nProduto {i+1}:")
        print(f"  Nome: {product.get('name')}")
        print(f"  Marca original: {product.get('brand')}")
        print(f"  Laboratório padronizado: {match['laboratory'] if match else 'N/A'}")
        print(f"  Tipo de match: {match['match_type'] if match else 'N/A'}")
        print(f"  Score: {match['similarity_score'] if match else 'N/A'}")

if __name__ == "__main__":
    main() 