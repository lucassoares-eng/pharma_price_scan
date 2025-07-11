import re
import logging
from .base_scraper import BaseScraper

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("DrogaRaiaScraper")

class DrogaRaiaScraper(BaseScraper):
    """Scraper para o site Droga Raia usando Selenium"""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.drogaraia.com.br",
            search_url="https://www.drogaraia.com.br/search",
            pharmacy_name="Droga Raia"
        )
    
    def search(self, medicine_description):
        """
        Busca medicamentos no site Droga Raia
        
        Args:
            medicine_description (str): Descrição do medicamento a ser buscado
            
        Returns:
            dict: Resultados da busca com produtos encontrados
        """
        try:
            # Preparar a query de busca
            url = self.create_search_url(medicine_description)
            self.logger.info(f"Buscando URL: {url}")
            
            # Fazer a requisição usando Selenium
            response = self.make_request(url)
            
            # Parsear o HTML
            soup = self.parse_html(response['content'])
            
            # Extrair produtos
            products = self._extract_products(soup)
            self.logger.info(f"Produtos encontrados: {len(products)}")
            
            return self.format_response(products, url)
            
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            return self.format_response([], "", f'Erro inesperado: {str(e)}')
        finally:
            # Limpar recursos
            self.cleanup()
    
    def _extract_products(self, soup):
        """
        Extrai produtos do HTML parseado
        
        Args:
            soup (BeautifulSoup): HTML parseado
            
        Returns:
            list: Lista de produtos extraídos
        """
        # Encontrar o container de produtos
        products_container = soup.find('div', {'data-testid': 'container-products'})
        
        if not products_container:
            self.logger.warning("Container de produtos não encontrado no HTML.")
            self.logger.debug(f"HTML da página (primeiros 1000 chars):\n{str(soup)[:1000]}")
            return []
        
        # Extrair produtos
        products = []
        product_articles = products_container.find_all('article', class_=lambda x: x and 'vertical' in x)
        self.logger.info(f"Quantidade de <article> encontrados: {len(product_articles)}")
        
        for article in product_articles:
            try:
                product = self._extract_product_info(article)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        
        return products
    
    def _extract_product_info(self, article):
        """
        Extrai informações de um produto do HTML
        
        Args:
            article: Elemento HTML do produto
            
        Returns:
            dict: Informações do produto ou None se não conseguir extrair
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
            if name_link:
                product_link = self.base_url + name_link.get('href', '')
            
            # Imagem do produto
            img_element = article.find('img', {'data-testid': 'product-image'})
            image_url = ""
            if img_element:
                image_url = img_element.get('src', '')
            
            # Verificar se há desconto
            discount_info = self._extract_discount_info(article)
            
            return {
                'name': name,
                'brand': brand,
                'description': description,
                'price': price_info['current_price'],
                'original_price': price_info['original_price'],
                'discount_percentage': discount_info['percentage'],
                'product_url': product_link,
                'image_url': image_url,
                'has_discount': discount_info['has_discount']
            }
            
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