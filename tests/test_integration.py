#!/usr/bin/env python3
"""
Teste de integração para verificar se o novo ProductUnifier está funcionando com os scrapers
"""

import sys
import os
import json
import requests

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_integration():
    """Teste de integração com a API"""
    print("=== Teste de Integração com API ===")
    
    # URL da API (assumindo que está rodando localmente)
    api_url = "http://localhost:5000/api/pharma/search"
    
    # Dados de teste
    test_data = {
        "medicine_description": "dipirona 1g 20 comprimidos"
    }
    
    try:
        print("1. Fazendo requisição para a API...")
        response = requests.post(api_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API respondeu com sucesso!")
            
            # Verificar se há resultados processados
            if 'processed_results' in result:
                print("✅ Resultados processados encontrados!")
                
                # Analisar resultados de cada farmácia
                for pharmacy_name, pharmacy_data in result['processed_results'].items():
                    print(f"\n📊 {pharmacy_name.upper()}:")
                    
                    if 'standardization_stats' in pharmacy_data:
                        stats = pharmacy_data['standardization_stats']
                        print(f"   - Total de produtos: {stats['total_products']}")
                        print(f"   - Produtos padronizados: {stats['standardized_products']}")
                        print(f"   - Taxa de padronização: {stats['standardization_rate']:.1f}%")
                    
                    if 'products' in pharmacy_data and pharmacy_data['products']:
                        print(f"   - Produtos encontrados: {len(pharmacy_data['products'])}")
                        
                        # Mostrar alguns produtos como exemplo
                        for i, product in enumerate(pharmacy_data['products'][:3]):
                            print(f"   Produto {i+1}:")
                            print(f"     Nome original: {product.get('name', 'N/A')}")
                            print(f"     Nome padronizado: {product.get('standardized_name', 'N/A')}")
                            print(f"     Laboratório: {product.get('laboratory', 'N/A')}")
                            print(f"     Score: {product.get('similarity_score', 0):.2f}")
                            print(f"     Tipo de match: {product.get('match_type', 'N/A')}")
                            print(f"     Padronizado: {product.get('is_standardized', False)}")
                
                print("\n✅ Integração funcionando corretamente!")
                return True
            else:
                print("❌ Resultados processados não encontrados na resposta")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que o servidor está rodando.")
        print("Para iniciar o servidor, execute: python app.py")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def test_unified_api():
    """Teste da API unificada"""
    print("\n=== Teste da API Unificada ===")
    
    # URL da API unificada
    api_url = "http://localhost:5000/api/pharma/search_unified"
    
    # Dados de teste
    test_data = {
        "medicine_description": "dipirona 1g 20 comprimidos"
    }
    
    try:
        print("1. Fazendo requisição para a API unificada...")
        response = requests.post(api_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API unificada respondeu com sucesso!")
            
            # Analisar resultados de cada farmácia
            for pharmacy_name, pharmacy_data in result.items():
                print(f"\n📊 {pharmacy_name.upper()}:")
                
                if 'standardization_stats' in pharmacy_data:
                    stats = pharmacy_data['standardization_stats']
                    print(f"   - Total de produtos: {stats['total_products']}")
                    print(f"   - Produtos padronizados: {stats['standardized_products']}")
                    print(f"   - Taxa de padronização: {stats['standardization_rate']:.1f}%")
                
                if 'products' in pharmacy_data and pharmacy_data['products']:
                    print(f"   - Produtos encontrados: {len(pharmacy_data['products'])}")
                    
                    # Mostrar alguns produtos como exemplo
                    for i, product in enumerate(pharmacy_data['products'][:3]):
                        print(f"   Produto {i+1}:")
                        print(f"     Nome original: {product.get('name', 'N/A')}")
                        print(f"     Nome padronizado: {product.get('standardized_name', 'N/A')}")
                        print(f"     Laboratório: {product.get('laboratory', 'N/A')}")
                        print(f"     Score: {product.get('similarity_score', 0):.2f}")
                        print(f"     Tipo de match: {product.get('match_type', 'N/A')}")
                        print(f"     Padronizado: {product.get('is_standardized', False)}")
            
            print("\n✅ API unificada funcionando corretamente!")
            return True
        else:
            print(f"❌ Erro na API unificada: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API unificada.")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste da API unificada: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste de Integração do ProductUnifier com Scrapers")
    print("=" * 60)
    
    # Teste da API principal
    success1 = test_api_integration()
    
    # Teste da API unificada
    success2 = test_unified_api()
    
    # Resultado final
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O novo ProductUnifier está integrado e funcionando corretamente com os scrapers!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("Verifique se o servidor está rodando e se há problemas na integração.")
    
    return success1 and success2

if __name__ == "__main__":
    main() 