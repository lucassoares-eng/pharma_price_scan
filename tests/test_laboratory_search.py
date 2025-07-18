#!/usr/bin/env python3
"""
Teste específico para busca por laboratório na descrição
"""

import sys
import os
import json

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def test_laboratory_search():
    """Teste específico para busca por laboratório"""
    print("=== Teste de Busca por Laboratório na Descrição ===")
    
    try:
        # Obter o caminho correto para o arquivo de marcas
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        brands_file_path = os.path.join(parent_dir, "static", "lista_marcas.csv")
        
        # Inicializar ProductUnifier com o caminho correto
        unifier = ProductUnifier(brands_file_path)
        
        # Testar com um produto específico que sabemos que tem laboratório na descrição
        test_product = {
            'name': 'Dipirona Sódica 1g 20 Comprimidos',
            'brand': 'Neo Química',
            'description': 'Analgésico e antitérmico fabricado pela NEO QUIMICA',
            'price': 8.90
        }
        
        print("1. Produto de teste:")
        print(f"   Nome: {test_product['name']}")
        print(f"   Marca: {test_product['brand']}")
        print(f"   Descrição: {test_product['description']}")
        print()
        
        # Testar normalização
        normalized_name = unifier.normalize_text(test_product['name'])
        normalized_brand = unifier.normalize_text(test_product['brand'])
        normalized_description = unifier.normalize_text(test_product['description'])
        
        print("2. Normalização:")
        print(f"   Nome normalizado: '{normalized_name}'")
        print(f"   Marca normalizada: '{normalized_brand}'")
        print(f"   Descrição normalizada: '{normalized_description}'")
        print()
        
        # Testar busca direta por laboratório
        print("3. Buscando laboratórios na descrição:")
        found_laboratories = []
        
        for brand_product, laboratory in unifier.brands_data.items():
            normalized_laboratory = unifier.normalize_text(laboratory)
            if normalized_laboratory in normalized_description:
                found_laboratories.append({
                    'laboratory': laboratory,
                    'normalized_laboratory': normalized_laboratory,
                    'brand_product': brand_product
                })
                print(f"   ✓ Encontrou '{normalized_laboratory}' (Lab: {laboratory})")
        
        if not found_laboratories:
            print("   ✗ Nenhum laboratório encontrado na descrição")
        print()
        
        # Testar busca por partes do laboratório
        print("4. Buscando por partes do laboratório:")
        partial_matches = []
        
        for brand_product, laboratory in unifier.brands_data.items():
            normalized_laboratory = unifier.normalize_text(laboratory)
            lab_words = normalized_laboratory.split()
            if len(lab_words) >= 2:
                found_words = sum(1 for word in lab_words if word in normalized_description)
                if found_words >= 2:
                    partial_matches.append({
                        'laboratory': laboratory,
                        'normalized_laboratory': normalized_laboratory,
                        'found_words': found_words,
                        'total_words': len(lab_words)
                    })
                    print(f"   ✓ Encontrou {found_words}/{len(lab_words)} palavras de '{normalized_laboratory}' (Lab: {laboratory})")
        
        if not partial_matches:
            print("   ✗ Nenhuma correspondência parcial encontrada")
        print()
        
        # Testar a função find_best_match diretamente
        print("5. Testando find_best_match:")
        match = unifier.find_best_match(
            test_product['name'],
            test_product['brand'],
            test_product['description']
        )
        
        if match:
            print(f"   ✓ Encontrou correspondência:")
            print(f"      Nome padronizado: {match['standardized_name']}")
            print(f"      Laboratório: {match['laboratory']}")
            print(f"      Score: {match['similarity_score']:.2f}")
            print(f"      Tipo: {match.get('match_type', 'unknown')}")
        else:
            print("   ✗ Nenhuma correspondência encontrada")
        print()
        
        # Testar com produtos que sabemos que têm laboratórios específicos
        print("6. Testando com produtos específicos:")
        specific_tests = [
            {
                'name': 'Dipirona Sódica 1g 20 Comprimidos',
                'brand': 'Neo Química',
                'description': 'Analgésico e antitérmico fabricado pela NEO QUIMICA',
                'expected_lab': 'NEO QUIMICA'
            },
            {
                'name': 'Dipirona 1g 20 Comprimidos',
                'brand': 'Prati Donaduzzi',
                'description': 'Analgésico e antitérmico da PRATI DONADUZZI',
                'expected_lab': 'PRATI DONADUZZI'
            }
        ]
        
        for i, test in enumerate(specific_tests, 1):
            print(f"   Teste {i}:")
            print(f"      Descrição: {test['description']}")
            print(f"      Laboratório esperado: {test['expected_lab']}")
            
            match = unifier.find_best_match(
                test['name'],
                test['brand'],
                test['description']
            )
            
            if match:
                print(f"      ✓ Encontrou: {match['laboratory']} (Score: {match['similarity_score']:.2f})")
                if match['laboratory'] == test['expected_lab']:
                    print(f"      ✓ Laboratório correto!")
                else:
                    print(f"      ✗ Laboratório incorreto. Esperado: {test['expected_lab']}")
            else:
                print(f"      ✗ Nenhuma correspondência encontrada")
            print()
        
        print("=== Teste de busca por laboratório concluído ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_laboratory_search()
    sys.exit(0 if success else 1) 