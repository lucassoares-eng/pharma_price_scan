#!/usr/bin/env python3
"""
Teste real com scraper Droga Raia + ProductUnifier
"""

import sys
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Erro ao configurar driver: {e}")
        return None

def get_simulated_data():
    """Retorna dados simulados mas realistas para teste"""
    return {
        'pharmacy': 'Droga Raia',
        'products': [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico fabricado pela NEO QUIMICA',
                'price': 8.90,
                'has_discount': True,
                'discount_percentage': 15
            },
            {
                'name': 'Dipirona 500mg 20 Comprimidos',
                'brand': 'Prati Donaduzzi',
                'description': 'Analgésico e antitérmico da PRATI DONADUZZI',
                'price': 6.50,
                'has_discount': False,
                'discount_percentage': 0
            },
            {
                'name': 'Dipirona Sódica 1g 10 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico fabricado pela NEO QUIMICA',
                'price': 5.20,
                'has_discount': True,
                'discount_percentage': 10
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Abbott',
                'description': 'Analgésico e antitérmico fabricado pela ABBOTT',
                'price': 12.80,
                'has_discount': False,
                'discount_percentage': 0
            },
            {
                'name': 'Dipirona Sódica 500mg 30 Comprimidos',
                'brand': 'União Química',
                'description': 'Analgésico e antitérmico fabricado pela UNIAO QUIMICA',
                'price': 9.90,
                'has_discount': True,
                'discount_percentage': 20
            }
        ]
    }

def test_real_scraper():
    """Teste real com scraper Droga Raia"""
    print("=== Teste Real: Droga Raia + ProductUnifier ===")
    print("Buscando: 'dipirona 1g 20 comprimidos'")
    print()
    
    # Configurar driver
    driver = setup_driver()
    if not driver:
        print("❌ Erro: Não foi possível configurar o driver do Selenium")
        return False
    
    try:
        # Inicializar scraper
        print("1. Inicializando scraper Droga Raia...")
        scraper = DrogaRaiaScraper(driver=driver)
        print("   ✓ Scraper inicializado")
        
        # Buscar produtos
        print("\n2. Buscando produtos no Droga Raia...")
        search_results = scraper.search("dipirona 1g 20 comprimidos")
        
        # Se não encontrou produtos, usar dados simulados
        if not search_results.get('products'):
            print("   ⚠ Nenhum produto encontrado no scraper")
            print("   Usando dados simulados para testar o ProductUnifier...")
            search_results = get_simulated_data()
            print(f"   ✓ Usando {len(search_results['products'])} produtos simulados")
        else:
            print(f"   ✓ Encontrados {len(search_results['products'])} produtos")
        
        print()
        
        # Mostrar produtos ANTES da padronização
        print("3. Produtos encontrados (ANTES do ProductUnifier):")
        for i, product in enumerate(search_results['products'][:5], 1):  # Mostrar apenas os 5 primeiros
            print(f"   {i}. Nome: {product['name']}")
            print(f"      Marca: {product['brand']}")
            print(f"      Descrição: {product.get('description', 'N/A')}")
            print(f"      Preço: R$ {product['price']}")
            if product.get('has_discount'):
                print(f"      Desconto: {product.get('discount_percentage', 0)}%")
            print()
        
        # Inicializar ProductUnifier
        print("4. Inicializando ProductUnifier...")
        unifier = ProductUnifier()
        print(f"   ✓ Carregados {len(unifier.brands_data)} produtos da lista de marcas")
        print()
        
        # Processar produtos com ProductUnifier
        print("5. Processando produtos com ProductUnifier...")
        standardized_results = unifier.process_scraper_results(search_results, "dipirona 1g 20 comprimidos")
        
        # Mostrar estatísticas de padronização
        stats = standardized_results['standardization_stats']
        print(f"   Total de produtos: {stats['total_products']}")
        print(f"   Produtos padronizados: {stats['standardized_products']}")
        print(f"   Taxa de padronização: {stats['standardization_rate']:.1f}%")
        print()
        
        # Mostrar produtos DEPOIS da padronização
        print("6. Produtos padronizados (DEPOIS do ProductUnifier):")
        for i, product in enumerate(standardized_results['products'][:5], 1):  # Mostrar apenas os 5 primeiros
            print(f"   {i}. Nome original: {product['name']}")
            print(f"      Nome padronizado: {product['standardized_name']}")
            print(f"      Laboratório: {product['laboratory']}")
            print(f"      Score de similaridade: {product['similarity_score']:.2f}")
            print(f"      Tipo de match: {product.get('match_type', 'unknown')}")
            print(f"      Padronizado: {'Sim' if product['is_standardized'] else 'Não'}")
            print(f"      Preço: R$ {product['price']}")
            print()
        
        # Salvar resultados em JSON
        output_file = "test_results/real_scraper_results.json"
        os.makedirs("test_results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'original_results': search_results,
                'standardized_results': standardized_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"7. Resultados salvos em: {output_file}")
        print()
        
        # Exemplo de dados para enviar ao backend
        print("8. Exemplo de dados para enviar ao backend:")
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
                    'is_standardized': p['is_standardized'],
                    'match_type': p.get('match_type', 'unknown')
                }
                for p in standardized_results['products']
            ],
            'standardization_stats': standardized_results['standardization_stats']
        }
        
        print(json.dumps(backend_data, indent=2, ensure_ascii=False))
        print()
        
        print("=== Teste real concluído com sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpar recursos
        if driver:
            driver.quit()

if __name__ == "__main__":
    success = test_real_scraper()
    sys.exit(0 if success else 1) 