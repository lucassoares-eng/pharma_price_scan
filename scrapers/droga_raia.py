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
                    self.logger.info(f"[DrogaRaiaScraper] Entrando no fluxo de extração de fabricante na página do produto: {product_link}")
                    extracted_brand = self._extract_brand_from_product_page(product_link)
                    self.logger.info(f"[DrogaRaiaScraper] Fabricante extraído da página do produto: {extracted_brand}")
                    final_brand = extracted_brand if extracted_brand else None
                    # Retorne o produto imediatamente, pois não faz sentido extrair outros campos de uma página de produto
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
                    self.logger.info(f"[DrogaRaiaScraper] Produto retornado após extração de fabricante: {product_data}")
                    return product_data
                else:
                    final_brand = found_lab_name or brand
            # Capitalizar brand, exceto EMS
            brand_value = final_brand
            if isinstance(brand_value, str) and brand_value.strip():
                if brand_value.strip().upper() == 'EMS':
                    brand_value = 'EMS'
                else:
                    brand_value = ' '.join([w.capitalize() for w in brand_value.strip().split()])
            product_data = {
                'name': name,
                'brand': brand_value,
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

    def _extract_brand_from_product_page(self, product_url):
        """
        Acessa a página do produto e tenta extrair a marca real, priorizando o Fabricante.
        """
        try:
            if not product_url:
                return None
            response = self.make_request(product_url)
            soup = self.parse_html(response['content'])
            # 1. Procurar pelo <li> cujo <span> seja 'Fabricante' (case insensitive, robusto)
            li_tags = soup.find_all('li')
            for li in li_tags:
                spans = li.find_all('span')
                if len(spans) >= 2:
                    label = spans[0].get_text(strip=True).lower()
                    if 'fabricante' in label:
                        # O valor pode estar em <span> ou <a> dentro do segundo span
                        value_span = spans[1]
                        a_tag = value_span.find('a')
                        if a_tag and a_tag.get_text(strip=True):
                            return a_tag.get_text(strip=True)
                        # Se não houver <a>, pegar texto do <span>
                        value_text = value_span.get_text(strip=True)
                        if value_text:
                            return value_text
            # 2. Se não achar, procurar pelo <li> cujo <span> seja 'Marca'
            for li in li_tags:
                spans = li.find_all('span')
                if len(spans) >= 2:
                    label = spans[0].get_text(strip=True).lower()
                    if 'marca' in label:
                        value_span = spans[1]
                        a_tag = value_span.find('a')
                        if a_tag and a_tag.get_text(strip=True):
                            return a_tag.get_text(strip=True)
                        value_text = value_span.get_text(strip=True)
                        if value_text:
                            return value_text
            # 3. Fallbacks antigos
            dt_tags = soup.find_all('dt')
            for dt in dt_tags:
                if 'marca' in dt.get_text(strip=True).lower() or 'fabricante' in dt.get_text(strip=True).lower():
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        return dd.get_text(strip=True)
            possible_labels = ['marca', 'fabricante']
            for label in possible_labels:
                label_elem = soup.find(string=lambda t: t and label in t.lower())
                if label_elem:
                    parent = label_elem.parent
                    if parent and parent.find_next_sibling():
                        return parent.find_next_sibling().get_text(strip=True)
            meta_brand = soup.find('meta', {'name': 'brand'})
            if meta_brand and meta_brand.get('content'):
                return meta_brand['content']
        except Exception as e:
            self.logger.error(f"Erro ao extrair marca da página do produto: {e}")
        return None 