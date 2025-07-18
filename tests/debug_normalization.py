#!/usr/bin/env python3
"""
Debug da normalização do ProductUnifier
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def debug_normalization():
    """Debug da normalização"""
    print("=== Debug da Normalização ===")
    
    try:
        # Inicializar ProductUnifier
        unifier = ProductUnifier()
        
        # Testar normalização
        test_cases = [
            "NEO QUIMICA",
            "PRATI DONADUZZI", 
            "EMS PHARMA",
            "CIMED",
            "MEDLEY"
        ]
        
        print("1. Testando normalização de laboratórios:")
        for lab in test_cases:
            normalized = unifier.normalize_text(lab)
            print(f"   '{lab}' → '{normalized}'")
        print()
        
        # Testar descrições
        test_descriptions = [
            "Analgésico e antitérmico fabricado pela NEO QUIMICA",
            "Analgésico e antitérmico da PRATI DONADUZZI",
            "Analgésico e antitérmico - EMS PHARMA",
            "Analgésico e antitérmico fabricado pela CIMED",
            "Analgésico e antitérmico da MEDLEY"
        ]
        
        print("2. Testando normalização de descrições:")
        for desc in test_descriptions:
            normalized = unifier.normalize_text(desc)
            print(f"   '{desc}' → '{normalized}'")
        print()
        
        # Testar busca de laboratórios
        print("3. Testando busca de laboratórios nas descrições:")
        for i, desc in enumerate(test_descriptions, 1):
            normalized_desc = unifier.normalize_text(desc)
            print(f"   Descrição {i}: '{normalized_desc}'")
            
            for lab in test_cases:
                normalized_lab = unifier.normalize_text(lab)
                if normalized_lab in normalized_desc:
                    print(f"     ✓ Encontrou '{normalized_lab}' em '{normalized_desc}'")
                else:
                    print(f"     ✗ Não encontrou '{normalized_lab}' em '{normalized_desc}'")
            print()
        
        # Testar busca por partes
        print("4. Testando busca por partes do laboratório:")
        for i, desc in enumerate(test_descriptions, 1):
            normalized_desc = unifier.normalize_text(desc)
            print(f"   Descrição {i}: '{normalized_desc}'")
            
            for lab in test_cases:
                normalized_lab = unifier.normalize_text(lab)
                lab_words = normalized_lab.split()
                if len(lab_words) >= 2:
                    found_words = sum(1 for word in lab_words if word in normalized_desc)
                    print(f"     '{normalized_lab}' → {found_words}/{len(lab_words)} palavras encontradas")
            print()
        
        print("=== Debug concluído ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_normalization()
    sys.exit(0 if success else 1) 