import re
import csv
import logging
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductUnifier:
    """Classe para padronizar nomes de produtos comparando com lista de laboratórios"""
    
    def __init__(self, brands_file_path: str = "static/laboratorios.csv"):
        self.brands_file_path = brands_file_path
        self.laboratories = self._load_laboratories()
        self.similarity_threshold = 0.5

    def _load_laboratories(self) -> set:
        """
        Carrega laboratórios únicos do arquivo CSV
        """
        laboratories = set()
        try:
            with open(self.brands_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    lab = row.get('laboratorio', '').strip()
                    if lab:
                        laboratories.add(lab)
            logger.info(f"Carregados {len(laboratories)} laboratórios da lista")
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo de laboratórios: {e}")
        return laboratories

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
    
    def identify_brand_from_name(self, product_name: str, search_term: str = "") -> str:
        if not product_name:
            return ""
        # Marca: apenas a primeira palavra do nome original, preservando hífens e capitalização
        original_words = product_name.split()
        def smart_capitalize(word):
            return '-'.join([w.capitalize() for w in word.split('-')])
        composed_brand = smart_capitalize(original_words[0])
        normalized_name = self.normalize_text(product_name)
        words = normalized_name.split()
        if not words:
            return ""
        first_word = words[0]
        if search_term:
            normalized_search = self.normalize_text(search_term)
            search_words = normalized_search.split()
            # Só busca laboratório no nome se o produto começa com a molécula buscada
            if search_words and first_word == search_words[0]:
                for laboratory in self.laboratories:
                    normalized_laboratory = self.normalize_text(laboratory)
                    if normalized_laboratory in normalized_name:
                        return laboratory  # Retorna exatamente como no CSV
                    elif len(normalized_laboratory) > 3:
                        lab_words = normalized_laboratory.split()
                        if len(lab_words) >= 2:
                            found_words = sum(1 for word in lab_words if word in normalized_name)
                            if found_words >= 2:
                                return laboratory
                return composed_brand
            else:
                return composed_brand
        else:
            return composed_brand

    def _lab_format(self, lab: str) -> str:
        words = [w for w in lab.replace('-', ' ').split() if w]
        if any(len(w) <= 3 for w in words):
            return lab.upper()
        else:
            return ' '.join([w.capitalize() for w in lab.split()])

    def _word_in_text(self, word, text):
        return re.search(r'\b' + re.escape(word) + r'\b', text) is not None

    def _is_similar(self, a: str, b: str, threshold: float = 0.8) -> bool:
        return SequenceMatcher(None, a, b).ratio() >= threshold

    def _first_word_brand(self, name: str) -> str:
        # Retorna a primeira palavra do nome original, preservando hífens e capitalização
        if not name:
            return ""
        first = name.split()[0]
        return '-'.join([w.capitalize() for w in first.split('-')])

    def find_best_match(self, product_name: str, product_brand: str = "", product_description: str = "", search_term: str = "") -> Optional[Dict[str, str]]:
        normalized_name = self.normalize_text(product_name)
        normalized_brand = self.normalize_text(product_brand)
        normalized_description = self.normalize_text(product_description)
        found_lab_in_name = None
        stopwords = set([
            'farma', 'generico', 'genérico', 'lab', 'laboratorio', 'laboratório', 'farmaceutica', 'farmacêutica', 'pharma', 'pharmaceutical', 'com', 'ind', 'indústria', 'industria', 'sa', 's/a', 'sa.', 's.a.'
        ])
        if search_term:
            normalized_search = self.normalize_text(search_term)
            search_words = normalized_search.split()
            words = normalized_name.split()
            # Se a primeira palavra do termo de busca for similar à primeira do nome, busca laboratório em todo o nome
            if search_words and words and self._is_similar(words[0], search_words[0]):
                for laboratory in self.laboratories:
                    normalized_laboratory = self.normalize_text(laboratory)
                    lab_words = normalized_laboratory.split()
                    for lab_word in lab_words:
                        if len(lab_word) >= 3 and lab_word not in stopwords and self._word_in_text(lab_word, normalized_name):
                            found_lab_in_name = laboratory
                            break
                    if found_lab_in_name:
                        break
        if found_lab_in_name:
            return {
                'standardized_name': product_name,
                'laboratory': self._lab_format(found_lab_in_name),
                'similarity_score': 1.0,
                'match_type': 'laboratory_in_name'
            }
        best_match = None
        found_laboratory_in_description = None
        if normalized_description:
            for laboratory in self.laboratories:
                normalized_laboratory = self.normalize_text(laboratory)
                lab_words = normalized_laboratory.split()
                for lab_word in lab_words:
                    if len(lab_word) >= 3 and lab_word not in stopwords and self._word_in_text(lab_word, normalized_description):
                        found_laboratory_in_description = laboratory
                        break
                if found_laboratory_in_description:
                    break
        if found_laboratory_in_description:
            best_match = {
                'standardized_name': product_name,
                'laboratory': self._lab_format(found_laboratory_in_description),
                'similarity_score': 1.0,
                'match_type': 'laboratory_in_description'
            }
        else:
            best_match = {
                'standardized_name': product_name,
                'laboratory': self._first_word_brand(product_name),
                'similarity_score': 1.0,
                'match_type': 'brand_identified'
            }
        return best_match
    
    def standardize_product_list(self, products: List[Dict[str, Any]], search_term: str = "") -> List[Dict[str, Any]]:
        """
        Padroniza uma lista de produtos comparando com a lista de marcas
        
        Args:
            products: Lista de produtos a serem padronizados
            
        Returns:
            Lista de produtos com nomes padronizados
        """
        standardized_products = []
        
        for product in products:
            try:
                # Criar cópia do produto para não modificar o original
                standardized_product = product.copy()
                
                # Buscar correspondência na lista de marcas
                match = self.find_best_match(
                    product.get('name', ''),
                    product.get('brand', ''),
                    product.get('description', ''),
                    search_term # Passar o search_term para o find_best_match
                )
                
                if match:
                    # Produto encontrado na lista de marcas
                    standardized_product['standardized_name'] = match['standardized_name']
                    standardized_product['laboratory'] = match['laboratory']
                    standardized_product['similarity_score'] = match['similarity_score']
                    standardized_product['match_type'] = match.get('match_type', 'unknown')
                    standardized_product['is_standardized'] = True
                else:
                    # Produto não encontrado na lista de marcas
                    standardized_product['standardized_name'] = product.get('name', '')
                    standardized_product['laboratory'] = product.get('brand', '')
                    standardized_product['similarity_score'] = 0.0
                    standardized_product['match_type'] = 'not_found'
                    standardized_product['is_standardized'] = False
                
                standardized_products.append(standardized_product)
                
            except Exception as e:
                logger.error(f"Erro ao padronizar produto {product.get('name', 'N/A')}: {e}")
                # Adicionar produto sem padronização em caso de erro
                product_copy = product.copy()
                product_copy['standardized_name'] = product.get('name', '')
                product_copy['laboratory'] = product.get('brand', '')
                product_copy['similarity_score'] = 0.0
                product_copy['match_type'] = 'error'
                product_copy['is_standardized'] = False
                standardized_products.append(product_copy)
        
        return standardized_products
    
    def process_scraper_results(self, scraper_results: Dict[str, Any], search_term: str = "") -> Dict[str, Any]:
        """
        Processa resultados de um scraper e padroniza os produtos
        
        Args:
            scraper_results: Resultados do scraper
            search_term: Termo de busca usado no scraper
            
        Returns:
            Resultados com produtos padronizados
        """
        try:
            # Verificar se há produtos nos resultados
            if 'products' not in scraper_results or not scraper_results['products']:
                logger.warning("Nenhum produto encontrado nos resultados do scraper")
                return scraper_results
            
            # Adicionar search_term aos produtos para uso na padronização
            for product in scraper_results['products']:
                product['search_term'] = search_term
            
            # Padronizar produtos
            standardized_products = self.standardize_product_list(scraper_results['products'], search_term)
            
            # Criar resultado padronizado
            standardized_results = scraper_results.copy()
            standardized_results['products'] = standardized_products
            
            # Adicionar estatísticas de padronização
            total_products = len(standardized_products)
            standardized_count = sum(1 for p in standardized_products if p.get('is_standardized', False))
            
            standardized_results['standardization_stats'] = {
                'total_products': total_products,
                'standardized_products': standardized_count,
                'standardization_rate': (standardized_count / total_products * 100) if total_products > 0 else 0
            }
            
            logger.info(f"Padronização concluída: {standardized_count}/{total_products} produtos padronizados")
            
            return standardized_results
            
        except Exception as e:
            logger.error(f"Erro ao processar resultados do scraper: {e}")
            return scraper_results

# Função de conveniência para uso direto
def standardize_products(products: List[Dict[str, Any]], brands_file_path: str = "static/lista_marcas.csv") -> List[Dict[str, Any]]:
    """
    Função de conveniência para padronizar produtos
    
    Args:
        products: Lista de produtos a serem padronizados
        brands_file_path: Caminho para o arquivo CSV com lista de marcas
        
    Returns:
        Lista de produtos com nomes padronizados
    """
    unifier = ProductUnifier(brands_file_path)
    return unifier.standardize_product_list(products) 