import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.product_unifier import ProductUnifier

def test_brand_similar_to_search_returns_none():
    """Testa se quando a primeira palavra da marca é similar à primeira palavra da busca, retorna brand como None"""
    
    # Criar unifier
    unifier = ProductUnifier("static/laboratorios.csv")
    
    # Teste 1: Brand "Dipirona Sodica" com search "dipirona" - deve retornar brand como None
    result1 = unifier.find_best_match(
        product_name="Dipirona Monoidratada 1g 20 comprimidos EMS Genérico",
        product_brand="Dipirona Sodica",
        product_description="20 Comprimidos",
        search_term="dipirona"
    )
    
    print("=== Teste 1: Brand similar à busca ===")
    print(f"Product: Dipirona Monoidratada 1g 20 comprimidos EMS Genérico")
    print(f"Brand: Dipirona Sodica")
    print(f"Search: dipirona")
    print(f"Result: {result1}")
    print(f"Brand should be None: {result1['brand'] is None}")
    print()
    
    # Teste 2: Brand "Ibuprofeno" com search "ibuprofeno" - deve retornar brand como None
    result2 = unifier.find_best_match(
        product_name="Ibuprofeno 600mg 20 comprimidos EMS",
        product_brand="Ibuprofeno",
        product_description="20 Comprimidos",
        search_term="ibuprofeno"
    )
    
    print("=== Teste 2: Brand igual à busca ===")
    print(f"Product: Ibuprofeno 600mg 20 comprimidos EMS")
    print(f"Brand: Ibuprofeno")
    print(f"Search: ibuprofeno")
    print(f"Result: {result2}")
    print(f"Brand should be None: {result2['brand'] is None}")
    print()
    
    # Teste 3: Brand "Paracetamol" com search "dipirona" - deve retornar brand normal
    result3 = unifier.find_best_match(
        product_name="Paracetamol 750mg 20 comprimidos EMS",
        product_brand="Paracetamol",
        product_description="20 Comprimidos",
        search_term="dipirona"
    )
    
    print("=== Teste 3: Brand diferente da busca ===")
    print(f"Product: Paracetamol 750mg 20 comprimidos EMS")
    print(f"Brand: Paracetamol")
    print(f"Search: dipirona")
    print(f"Result: {result3}")
    print(f"Brand should NOT be None: {result3['brand'] is not None}")
    print()
    
    # Teste 4: Brand "Dipiriona" (typo) com search "dipirona" - deve retornar brand como None
    result4 = unifier.find_best_match(
        product_name="Dipiriona Monoidratada 1g 20 comprimidos EMS Genérico",
        product_brand="Dipiriona Sodica",
        product_description="20 Comprimidos",
        search_term="dipirona"
    )
    
    print("=== Teste 4: Brand com typo similar à busca ===")
    print(f"Product: Dipiriona Monoidratada 1g 20 comprimidos EMS Genérico")
    print(f"Brand: Dipiriona Sodica")
    print(f"Search: dipirona")
    print(f"Result: {result4}")
    print(f"Brand should be None: {result4['brand'] is None}")
    print()
    
    # Verificar se os testes passaram
    assert result1['brand'] is None, f"Teste 1 falhou: brand deveria ser None, mas foi {result1['brand']}"
    assert result2['brand'] is None, f"Teste 2 falhou: brand deveria ser None, mas foi {result2['brand']}"
    assert result3['brand'] is not None, f"Teste 3 falhou: brand não deveria ser None, mas foi {result3['brand']}"
    assert result4['brand'] is None, f"Teste 4 falhou: brand deveria ser None, mas foi {result4['brand']}"
    
    print("✅ Todos os testes passaram!")

if __name__ == "__main__":
    test_brand_similar_to_search_returns_none() 