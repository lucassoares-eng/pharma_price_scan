#!/usr/bin/env python3
"""
Exemplo de integração do Pharma Price Scanner
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.droga_raia import DrogaRaiaScraper
from scrapers.sao_joao import SaoJoaoScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

def test_all_scrapers():
    """Testa todos os scrapers disponíveis"""
    
    print("=== Teste de Integração do Pharma Price Scanner ===\n")
    
    # Configurar driver compartilhado
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Lista de scrapers para testar
        scrapers = {
            'Droga Raia': DrogaRaiaScraper(driver=driver),
            'São João': SaoJoaoScraper(driver=driver)
        }
        
        # Medicamento para teste
        test_medicine = "ibuprofeno 600mg 20"
        
        results = {}
        
        for pharmacy_name, scraper in scrapers.items():
            print(f"Testando {pharmacy_name}...")
            
            try:
                result = scraper.search(test_medicine)
                results[pharmacy_name] = result
                
                print(f"✓ {pharmacy_name}: {result.get('total_products', 0)} produtos encontrados")
                
                if result.get('error'):
                    print(f"  Erro: {result['error']}")
                else:
                    # Mostrar produtos mais baratos
                    products = result.get('products', [])
                    if products:
                        cheapest = products[0]  # Já ordenado por preço
                        print(f"  Mais barato: {cheapest.get('name', 'N/A')} - R$ {cheapest.get('price', 'N/A')}")
                
            except Exception as e:
                print(f"✗ {pharmacy_name}: Erro - {e}")
                results[pharmacy_name] = {'error': str(e), 'products': []}
            
            print()
        
        # Salvar resultados
        with open('integration_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("Resultados salvos em: integration_test_results.json")
        
        # Resumo
        print("\n=== Resumo ===")
        for pharmacy_name, result in results.items():
            if result.get('error'):
                print(f"{pharmacy_name}: ❌ {result['error']}")
            else:
                total = result.get('total_products', 0)
                print(f"{pharmacy_name}: ✅ {total} produtos")
        
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("Driver encerrado")

if __name__ == "__main__":
    test_all_scrapers() 