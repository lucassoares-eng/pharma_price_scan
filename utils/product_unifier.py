import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductUnifier:
    """Classe para unificar produtos semelhantes de diferentes farmácias"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Inicializa o unificador de produtos
        
        Args:
            similarity_threshold: Limiar de similaridade para considerar produtos iguais (0.0 a 1.0)
        """
        self.similarity_threshold = similarity_threshold
    
    def normalize_text(self, text: str) -> str:
        """
        Normaliza texto para comparação
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover acentos e caracteres especiais
        text = re.sub(r'[áàâãä]', 'a', text)
        text = re.sub(r'[éèêë]', 'e', text)
        text = re.sub(r'[íìîï]', 'i', text)
        text = re.sub(r'[óòôõö]', 'o', text)
        text = re.sub(r'[úùûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        
        # Remover caracteres especiais mantendo apenas letras, números e espaços
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remover espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_key_info(self, product: Dict[str, Any]) -> Dict[str, str]:
        """
        Extrai informações-chave do produto para comparação
        
        Args:
            product: Dicionário do produto
            
        Returns:
            Dicionário com informações-chave normalizadas
        """
        name = self.normalize_text(product.get('name', ''))
        brand = self.normalize_text(product.get('brand', ''))
        description = self.normalize_text(product.get('description', ''))
        
        # Extrair informações específicas de medicamentos
        dosage = ""
        quantity = ""
        
        # Padrões para extrair dosagem e quantidade
        dosage_patterns = [
            r'(\d+)\s*mg',
            r'(\d+)\s*mcg',
            r'(\d+)\s*g',
            r'(\d+)\s*ml',
        ]
        
        quantity_patterns = [
            r'(\d+)\s*comprimidos?',
            r'(\d+)\s*capsulas?',
            r'(\d+)\s*tablets?',
            r'(\d+)\s*ml',
            r'(\d+)\s*gotas?',
        ]
        
        # Buscar dosagem
        for pattern in dosage_patterns:
            match = re.search(pattern, name + ' ' + description)
            if match:
                dosage = match.group(1)
                break
        
        # Buscar quantidade
        for pattern in quantity_patterns:
            match = re.search(pattern, name + ' ' + description)
            if match:
                quantity = match.group(1)
                break
        
        return {
            'name': name,
            'brand': brand,
            'description': description,
            'dosage': dosage,
            'quantity': quantity
        }
    
    def calculate_similarity(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> float:
        """
        Calcula a similaridade entre dois produtos
        
        Args:
            product1: Primeiro produto
            product2: Segundo produto
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        info1 = self.extract_key_info(product1)
        info2 = self.extract_key_info(product2)
        
        # Pesos para diferentes campos
        weights = {
            'name': 0.4,
            'brand': 0.3,
            'description': 0.2,
            'dosage': 0.05,
            'quantity': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for field, weight in weights.items():
            if info1[field] and info2[field]:
                # Calcular similaridade usando SequenceMatcher
                similarity = SequenceMatcher(None, info1[field], info2[field]).ratio()
                
                # Bônus para correspondência exata
                if info1[field] == info2[field]:
                    similarity = 1.0
                
                total_score += similarity * weight
                total_weight += weight
        
        # Se não há campos para comparar, retornar 0
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def find_similar_products(self, products: List[Dict[str, Any]]) -> List[List[int]]:
        """
        Encontra grupos de produtos semelhantes
        
        Args:
            products: Lista de produtos
            
        Returns:
            Lista de grupos (cada grupo é uma lista de índices)
        """
        groups = []
        used_indices = set()
        
        for i in range(len(products)):
            if i in used_indices:
                continue
            
            current_group = [i]
            used_indices.add(i)
            
            for j in range(i + 1, len(products)):
                if j in used_indices:
                    continue
                
                similarity = self.calculate_similarity(products[i], products[j])
                
                if similarity >= self.similarity_threshold:
                    current_group.append(j)
                    used_indices.add(j)
            
            if len(current_group) > 1:
                groups.append(current_group)
        
        return groups
    
    def unify_products(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unifica produtos semelhantes de diferentes farmácias
        
        Args:
            results: Resultados das buscas das farmácias
            
        Returns:
            Resultados unificados
        """
        try:
            # Coletar todos os produtos de todas as farmácias
            all_products = []
            pharmacy_mapping = {}  # Mapeia índice do produto para farmácia
            
            for pharmacy_name, pharmacy_data in results.items():
                if 'products' in pharmacy_data and isinstance(pharmacy_data['products'], list):
                    for product in pharmacy_data['products']:
                        # Adicionar informação da farmácia ao produto
                        product_with_pharmacy = product.copy()
                        product_with_pharmacy['pharmacy'] = pharmacy_name
                        product_with_pharmacy['pharmacy_display_name'] = pharmacy_data.get('pharmacy', pharmacy_name)
                        
                        all_products.append(product_with_pharmacy)
                        pharmacy_mapping[len(all_products) - 1] = pharmacy_name
            
            if not all_products:
                return results
            
            # Encontrar grupos de produtos semelhantes
            similar_groups = self.find_similar_products(all_products)
            
            # Criar produtos unificados
            unified_products = []
            
            # Processar produtos que não foram agrupados
            processed_indices = set()
            for group in similar_groups:
                processed_indices.update(group)
            
            # Adicionar produtos não agrupados
            for i, product in enumerate(all_products):
                if i not in processed_indices:
                    unified_products.append({
                        'unified_name': product['name'],
                        'unified_brand': product['brand'],
                        'unified_description': product['description'],
                        'variants': [product],
                        'best_price': product['price'],
                        'best_price_pharmacy': product['pharmacy'],
                        'has_discount': product.get('has_discount', False),
                        'total_variants': 1
                    })
            
            # Processar grupos de produtos semelhantes
            for group in similar_groups:
                if len(group) == 0:
                    continue
                
                group_products = [all_products[i] for i in group]
                
                # Encontrar o produto com melhor preço
                best_price_product = min(group_products, key=lambda p: p['price'])
                
                # Criar nome unificado (usar o mais descritivo)
                names = [p['name'] for p in group_products]
                unified_name = max(names, key=len)  # Usar o nome mais longo
                
                # Criar marca unificada
                brands = [p['brand'] for p in group_products if p.get('brand')]
                unified_brand = brands[0] if brands else ""
                
                # Criar descrição unificada
                descriptions = [p['description'] for p in group_products if p.get('description')]
                unified_description = descriptions[0] if descriptions else ""
                
                unified_products.append({
                    'unified_name': unified_name,
                    'unified_brand': unified_brand,
                    'unified_description': unified_description,
                    'variants': group_products,
                    'best_price': best_price_product['price'],
                    'best_price_pharmacy': best_price_product['pharmacy'],
                    'has_discount': any(p.get('has_discount', False) for p in group_products),
                    'total_variants': len(group_products)
                })
            
            # Ordenar por melhor preço
            unified_products.sort(key=lambda p: p['best_price'])
            
            # Criar resultado unificado
            unified_results = {
                'medicine_description': results.get('medicine_description', ''),
                'unified_products': unified_products,
                'total_unified_products': len(unified_products),
                'original_results': results  # Manter resultados originais para referência
            }
            
            logger.info(f"Unificados {len(all_products)} produtos em {len(unified_products)} grupos")
            
            return unified_results
            
        except Exception as e:
            logger.error(f"Erro ao unificar produtos: {e}")
            return results

def unify_pharmacy_results(results: Dict[str, Any], similarity_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Função de conveniência para unificar resultados de farmácias
    
    Args:
        results: Resultados das buscas das farmácias
        similarity_threshold: Limiar de similaridade
        
    Returns:
        Resultados unificados
    """
    unifier = ProductUnifier(similarity_threshold=similarity_threshold)
    return unifier.unify_products(results) 