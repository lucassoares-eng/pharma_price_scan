import re
import logging
from .base_scraper import BaseScraper
from utils.product_unifier import ProductUnifier

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("DrogaRaiaScraper")

class DrogaRaiaScraper(BaseScraper):
    """Scraper para o site Droga Raia usando Selenium"""
    
    def __init__(self, driver=None):
        super().__init__(
            base_url="https://www.drogaraia.com.br",
            search_url="https://www.drogaraia.com.br/search",
            pharmacy_name="Droga Raia",
            driver=driver
        )
        self.product_unifier = ProductUnifier()  # Instância única

    def search(self, medicine_description):
        """
        Busca medicamentos no site Droga Raia
        """
        try:
            url = self.create_search_url(medicine_description)
            self.logger.info(f"Buscando URL: {url}")
            response = self.make_request(url)
            soup = self.parse_html(response['content'])
            products = self._extract_products(soup, medicine_description)
            self.logger.info(f"Produtos encontrados: {len(products)}")
            products = sorted(
                products,
                key=lambda p: p['price'] if isinstance(p['price'], (int, float)) else float('inf')
            )
            return self.format_response(products, url)
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            return self.format_response([], "", f'Erro inesperado: {str(e)}')

    def _extract_products(self, soup, search_term):
        """
        Extrai produtos do HTML parseado
        """
        products_container = soup.find('div', {'data-testid': 'container-products'})
        if not products_container:
            self.logger.warning("Container de produtos não encontrado no HTML.")
            self.logger.debug(f"HTML da página (primeiros 1000 chars):\n{str(soup)[:1000]}")
            return []
        products = []
        product_articles = products_container.find_all('article', class_=lambda x: x and 'vertical' in x)
        self.logger.info(f"Quantidade de <article> encontrados: {len(product_articles)}")
        for idx, article in enumerate(product_articles, 1):
            try:
                product = self._extract_product_info(article, idx, search_term)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        return products

    def _extract_product_info(self, article, position=None, search_term=None):
        """
        Extrai informações de um produto do HTML
        """
        try:
            # Nome do produto
            name_element = article.find('h2', class_=lambda x: x and 'eGzxuI' in x)
            if name_element:
                name_link = name_element.find('a')
                name = name_link.get_text(strip=True) if name_link else name_element.get_text(strip=True)
            else:
                name = "Nome não disponível"
            # Marca/Fabricante
            brand_element = article.find('a', class_=lambda x: x and 'fibMCW' in x)
            brand = brand_element.get_text(strip=True) if brand_element else "Marca não disponível"
            # Descrição/Quantidade
            description_element = article.find('div', class_=lambda x: x and 'jJbyoN' in x)
            description = ""
            if description_element:
                desc_p = description_element.find('p')
                description = desc_p.get_text(strip=True) if desc_p else description_element.get_text(strip=True)
            # Preço
            price_info = self._extract_price(article)
            # Link do produto
            product_link = ""
            if name_element:
                name_link = name_element.find('a')
                if name_link:
                    product_link = self.base_url + name_link.get('href', '')
            # Imagem do produto
            img_element = article.find('img', {'data-testid': 'product-image'})
            image_url = ""
            if img_element:
                image_url = img_element.get('src', '')
            # Verificar se há desconto
            discount_info = self._extract_discount_info(article)
            # --- Lógica de busca condicional ---
            final_brand = brand
            if name and search_term:
                normalized_name = name.lower().strip()
                normalized_search = search_term.lower().strip()
                first_word = normalized_name.split()[0] if normalized_name.split() else ""
                found_lab = self.product_unifier.find_best_match(
                    product_name=name,
                    product_brand=brand,
                    product_description=description,
                    search_term=search_term
                )
                found_lab_name = found_lab['laboratory'] if found_lab and found_lab.get('laboratory') else ""
                if first_word == normalized_search.split()[0] and not found_lab_name:
                    # Buscar página específica (exemplo: extrair marca real da página do produto)
                    # Aqui você pode implementar a lógica de acessar a página do produto se necessário
                    # Exemplo: final_brand = self._extract_brand_from_product_page(product_link)
                    pass  # Placeholder para lógica real se necessário
                else:
                    final_brand = found_lab_name or brand
            product_data = {
                'name': name,
                'brand': final_brand,
                'description': description,
                'price': price_info['current_price'],
                'original_price': price_info['original_price'],
                'discount_percentage': discount_info['percentage'],
                'product_url': product_link,
                'has_discount': discount_info['has_discount'],
                'position': position
            }
            return product_data
        except Exception as e:
            self.logger.error(f"Erro ao extrair informações do produto: {e}")
            return None
    
    def _extract_price(self, article):
        """Extrai informações de preço do produto"""
        try:
            # Verificar se há desconto (preço com desconto)
            discount_price_container = article.find('div', {'data-testid': 'price-discount'})
            
            if discount_price_container:
                # Produto com desconto
                original_price_elem = discount_price_container.find('div', class_=lambda x: x and 'bZuLpF' in x)
                current_price_elem = discount_price_container.find('div', class_=lambda x: x and 'hsAtyD' in x)
                
                original_price = self._extract_price_value(original_price_elem)
                current_price = self._extract_price_value(current_price_elem)
                
                return {
                    'current_price': current_price,
                    'original_price': original_price
                }
            else:
                # Produto sem desconto
                price_elem = article.find('div', class_=lambda x: x and 'hUuLwk' in x)
                price = self._extract_price_value(price_elem)
                
                return {
                    'current_price': price,
                    'original_price': price
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair preço: {e}")
            return {
                'current_price': "Preço não disponível",
                'original_price': "Preço não disponível"
            }
    
    def _extract_price_value(self, price_element):
        """Extrai o valor do preço de um elemento"""
        if not price_element:
            return "Preço não disponível"
        
        price_text = price_element.get_text(strip=True)
        # Remover "R$" e espaços, converter para float
        price_match = re.search(r'R\$\s*([\d,]+)', price_text)
        if price_match:
            price_str = price_match.group(1).replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                return price_text
        return price_text
    
    def _extract_discount_info(self, article):
        """Extrai informações de desconto do produto"""
        try:
            # Verificar se há tag de desconto
            discount_tag = article.find('div', class_=lambda x: x and 'bogZNT' in x)
            
            if discount_tag:
                # Encontrar a porcentagem de desconto
                discount_div = discount_tag.find('div')
                if discount_div:
                    discount_text = discount_div.get_text(strip=True)
                    # Extrair apenas números
                    discount_match = re.search(r'(\d+)%', discount_text)
                    if discount_match:
                        return {
                            'has_discount': True,
                            'percentage': int(discount_match.group(1))
                        }
            
            return {
                'has_discount': False,
                'percentage': 0
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair desconto: {e}")
            return {
                'has_discount': False,
                'percentage': 0
            } 