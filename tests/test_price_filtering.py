#!/usr/bin/env python3
"""
Teste para verificar se produtos com preço zero são filtrados corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import process_pharmacy_results

def test_price_filtering():
    """Testa se produtos com preço zero são removidos"""
    
    # Dados de teste com produtos que têm preço zero
    test_results = {
        'droga_raia': {
            'pharmacy': 'Droga Raia',
            'products': [
                {
                    'name': 'Losartana Potássica 50mg 30 comprimidos Teuto Genérico',
                    'brand': 'Teuto Brasileiro',
                    'description': '30 Comprimidos Revestidos',
                    'price': 0,  # Preço zero - deve ser removido
                    'original_price': 0,
                    'position': 22,
                    'has_discount': False,
                    'discount_percentage': 0
                },
                {
                    'name': 'Dipirona 500mg 20 comprimidos',
                    'brand': 'Neo Química',
                    'description': '20 Comprimidos',
                    'price': 15.90,  # Preço válido - deve ser mantido
                    'original_price': 15.90,
                    'position': 1,
                    'has_discount': False,
                    'discount_percentage': 0
                },
                {
                    'name': 'Paracetamol 750mg 10 comprimidos',
                    'brand': 'EMS',
                    'description': '10 Comprimidos',
                    'price': None,  # Preço None - deve ser removido
                    'original_price': None,
                    'position': 5,
                    'has_discount': False,
                    'discount_percentage': 0
                }
            ]
        }
    }
    
    print("🧪 Testando filtragem de produtos com preço zero...")
    print()
    
    # Processar resultados
    processed_results = process_pharmacy_results(test_results, "dipirona")
    
    # Verificar resultados
    pharmacy_data = processed_results['droga_raia']
    products = pharmacy_data['products']
    
    print(f"📊 Resultados:")
    print(f"   - Produtos originais: {len(test_results['droga_raia']['products'])}")
    print(f"   - Produtos após filtragem: {len(products)}")
    print()
    
    # Verificar se produtos com preço zero foram removidos
    zero_price_products = [p for p in products if p.get('price', 0) == 0 or p.get('price') is None]
    valid_price_products = [p for p in products if p.get('price', 0) > 0]
    
    print(f"   - Produtos com preço zero/None: {len(zero_price_products)}")
    print(f"   - Produtos com preço válido: {len(valid_price_products)}")
    print()
    
    if len(zero_price_products) == 0:
        print("✅ SUCCESS: Todos os produtos com preço zero foram removidos!")
    else:
        print("❌ ERROR: Produtos com preço zero ainda estão presentes!")
        for product in zero_price_products:
            print(f"      - {product.get('name', 'N/A')}: R$ {product.get('price', 'N/A')}")
    
    if len(valid_price_products) == 1:
        print("✅ SUCCESS: Produto com preço válido foi mantido!")
        print(f"      - {valid_price_products[0].get('name', 'N/A')}: R$ {valid_price_products[0].get('price', 'N/A')}")
    else:
        print("❌ ERROR: Produto com preço válido não foi mantido corretamente!")
    
    print()
    print("🎯 Teste concluído!")

if __name__ == '__main__':
    test_price_filtering() 