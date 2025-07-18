#!/usr/bin/env python3
"""
Teste de import do ProductUnifier
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testando imports...")

try:
    print("1. Importando ProductUnifier...")
    from utils.product_unifier import ProductUnifier
    print("   ✓ ProductUnifier importado com sucesso")
    
    print("2. Criando instância...")
    unifier = ProductUnifier()
    print("   ✓ Instância criada com sucesso")
    
    print("3. Verificando dados carregados...")
    print(f"   ✓ {len(unifier.brands_data)} produtos carregados")
    
    print("4. Testando normalização...")
    result = unifier.normalize_text("Dipirona Sódica")
    print(f"   ✓ Normalização: '{result}'")
    
    print("\n=== Todos os testes passaram! ===")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc() 