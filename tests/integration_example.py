#!/usr/bin/env python3
"""
Exemplo de integração do ProductUnifier com o scraper Droga Raia
Demonstra como padronizar produtos após a busca
"""

import sys
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.droga_raia import DrogaRaiaScraper
from utils.product_unifier import ProductUnifier

def setup_driver():
    """Configura o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar em modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Erro ao configurar driver: {e}")
        return None

def main():
    """Função principal do exemplo"""
    print("=== Exemplo de Integração ProductUnifier + Droga Raia ===")
    print("Buscando: 'dipirona 1g 20 comprimidos'")
    print()
    
    # Configurar driver
    driver = setup_driver()
    if not driver:
        print("Erro: Não foi possível configurar o driver do Selenium")
        return
    
    try:
        # Inicializar scraper
        scraper = DrogaRaiaScraper(driver=driver)
        
        # Buscar produtos
        print("1. Buscando produtos no Droga Raia...")
        search_results = scraper.search("dipirona 1g 20 comprimidos")
        
        if not search_results.get('products'):
            print("Nenhum produto encontrado!")
            return
        
        print(f"   Encontrados {len(search_results['products'])} produtos")
        print()
        
        # Mostrar produtos originais
        print("2. Produtos encontrados (antes da padronização):")
        for i, product in enumerate(search_results['products'][:3], 1):  # Mostrar apenas os 3 primeiros
            print(f"   {i}. {product['name']} - {product['brand']}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Inicializar ProductUnifier
        print("3. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        print()
        
        # Padronizar produtos
        print("4. Padronizando produtos...")
        standardized_results = unifier.process_scraper_results(search_results)
        
        # Mostrar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        print(f"   Total de produtos: {stats['total_products']}")
        print(f"   Produtos padronizados: {stats['standardized_products']}")
        print(f"   Taxa de padronização: {stats['standardization_rate']:.1f}%")
        print()
        
        # Mostrar produtos padronizados
        print("5. Produtos padronizados:")
        for i, product in enumerate(standardized_results['products'][:3], 1):  # Mostrar apenas os 3 primeiros
            print(f"   {i}. Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score de similaridade: {product['similarity_score']:.2f}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Salvar resultados em JSON para análise
        output_file = "test_results/standardized_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_results, f, indent=2, ensure_ascii=False)
        
        print(f"6. Resultados salvos em: {output_file}")
        print()
        
        # Exemplo de como enviar para o backend
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
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpar recursos
        if driver:
            driver.quit()

if __name__ == "__main__":
    main() 