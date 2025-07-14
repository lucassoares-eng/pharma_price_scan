#!/usr/bin/env python3
"""
Teste específico para o scraper São João melhorado
"""

import sys
import os
import json
import time

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.sao_joao import SaoJoaoScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_sao_joao_improved():
    """Testa o scraper São João melhorado"""
    
    print("=== Teste do Scraper São João Melhorado ===\n")
    
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Criar scraper
        scraper = SaoJoaoScraper(driver=driver)
        
        # Testar busca
        medicine_description = "ibuprofeno 600mg 20 comprimidos"
        print(f"1. Buscando: {medicine_description}")
        
        results = scraper.search(medicine_description)
        
        print(f"2. Resultados obtidos:")
        print(f"   URL: {results.get('url', 'N/A')}")
        print(f"   Total de produtos: {results.get('total_products', 0)}")
        
        if 'products' in results and results['products']:
            print(f"\n3. Produtos encontrados:")
            for i, product in enumerate(results['products'], 1):
                print(f"\n   Produto {i}:")
                print(f"     Nome: {product.get('name', 'N/A')}")
                print(f"     Marca: {product.get('brand', 'N/A')}")
                print(f"     Preço: R$ {product.get('price', 'N/A')}")
                print(f"     URL: {product.get('product_url', 'N/A')}")
                
                # Verificar se a marca foi extraída corretamente
                if product.get('brand') and product.get('brand') != "Marca não disponível":
                    print(f"     ✅ Marca extraída com sucesso: {product['brand']}")
                else:
                    print(f"     ❌ Marca não foi extraída corretamente")
        
        # Salvar resultados em arquivo
        with open('test_sao_joao_improved_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n4. Resultados salvos em 'test_sao_joao_improved_results.json'")
        
        # Fechar driver
        driver.quit()
        
        return results
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        return None

if __name__ == "__main__":
    test_sao_joao_improved() 