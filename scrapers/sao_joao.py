import re
import logging
import time
from .base_scraper import BaseScraper
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("SaoJoaoScraper")

class SaoJoaoScraper(BaseScraper):
    """Scraper para o site São João usando Selenium"""
    
    def __init__(self, driver=None):
        super().__init__(
            base_url="https://www.saojoaofarmacias.com.br",
            search_url="https://www.saojoaofarmacias.com.br",
            pharmacy_name="São João",
            driver=driver
        )
    
    def search(self, medicine_description):
        """
        Busca medicamentos no site São João
        
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
            soup = self.parse_html(response)
            
            # Extrair produtos
            products = self._extract_products(soup)
            self.logger.info(f"Produtos encontrados: {len(products)}")

            # Ordenar produtos do menor para o maior preço
            products = sorted(
                products,
                key=lambda p: p['price'] if isinstance(p['price'], (int, float)) else float('inf')
            )
            
            return self.format_response(products, url)
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            return self.format_response([], "", f'Erro inesperado: {str(e)}')
        # Garantia extra: nunca retorna None
        return self.format_response([], "", "Erro desconhecido")
    
    def create_search_url(self, medicine_description):
        """
        Cria a URL de busca específica para o São João
        
        Args:
            medicine_description (str): Descrição do medicamento
            
        Returns:
            str: URL de busca
        """
        # Usar quote_plus mas substituir + por %20 para o São João
        search_query = quote_plus(medicine_description).replace('+', '%20')
        return f"{self.search_url}/{search_query}?_q={search_query}&map=ft"
    
    def make_request(self, url, timeout=30):
        """
        Abre a URL no Selenium, aceita cookies se necessário e espera o carregamento do container de produtos.
        """
        try:
            # Verificar se o driver está inicializado
            if not self.driver:
                self.logger.info("Driver não inicializado, configurando...")
                self._setup_driver()
            
            self.driver.get(url)
            self.logger.info(f"Página carregada: {url}")
            
            # Tentar aceitar cookies se o botão existir
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(translate(., 'ACEITAR', 'aceitar'), 'aceitar') or contains(., 'Aceitar') or contains(., 'OK') or contains(., 'Ok') or contains(., 'ok') or contains(., 'Concordo') or contains(., 'concordo')]")
                    )
                ).click()
                self.logger.info("Cookies aceitos")
            except Exception:
                self.logger.info("Nenhum popup de cookies encontrado")
            
            # Espera até o container de produtos aparecer
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "vtex-search-result-3-x-gallery"))
                )
                self.logger.info("Container de produtos encontrado")
            except Exception as e:
                self.logger.warning(f"Container de produtos não encontrado após {timeout}s: {e}")
            
            # Aguardar um pouco mais para garantir carregamento completo
            time.sleep(3)
            
            page_source = self.driver.page_source
            self.logger.info(f"HTML obtido com {len(page_source)} caracteres")
            return page_source
            
        except Exception as e:
            self.logger.error(f"Erro no make_request: {e}")
            # Retornar HTML vazio em caso de erro
            return "<html><body></body></html>"
    
    def _extract_products(self, soup):
        """
        Extrai produtos do HTML parseado
        
        Args:
            soup (BeautifulSoup): HTML parseado
            
        Returns:
            list: Lista de produtos extraídos
        """
        # Encontrar o container de produtos (gallery)
        products_container = soup.find('div', class_='vtex-search-result-3-x-gallery')
        
        if not products_container:
            self.logger.warning("Container de produtos não encontrado no HTML.")
            self.logger.debug(f"HTML da página (primeiros 1000 chars):\n{str(soup)[:1000]}")
            return []
        
        # Extrair produtos
        products = []
        product_sections = products_container.find_all('section', class_='vtex-product-summary-2-x-container')
        self.logger.info(f"Quantidade de seções de produtos encontradas: {len(product_sections)}")
        
        for idx, section in enumerate(product_sections, 1):
            try:
                product = self._extract_product_info(section, idx)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        
        return products
    
    def _extract_product_info(self, section, position=None):
        """
        Extrai informações de um produto do HTML
        
        Args:
            section: Elemento HTML da seção do produto
            
        Returns:
            dict: Informações do produto ou None se não conseguir extrair
        """
        try:
            # Nome do produto
            name_element = section.find('span', class_='vtex-product-summary-2-x-productBrand')
            name = name_element.get_text(strip=True) if name_element else "Nome não disponível"
            
            # Marca/Fabricante - extrair da classe ou do nome
            brand = "Marca não disponível"
            if name and "Genérico" in name:
                # Tentar extrair a marca do nome do produto
                brand_match = re.search(r'Genérico\s+([^-]+)', name)
                if brand_match:
                    brand = brand_match.group(1).strip()
                else:
                    brand = "Genérico"
            elif name:
                # Tentar extrair marca do início do nome
                brand_match = re.search(r'^([^-]+)', name)
                if brand_match:
                    brand = brand_match.group(1).strip()
            
            # Descrição/Quantidade - extrair do nome
            description = ""
            if name:
                # Tentar extrair quantidade e forma farmacêutica
                desc_match = re.search(r'(\d+mg?\s+\d+\s+\w+)', name)
                if desc_match:
                    description = desc_match.group(1)
            
            # Preço
            price_info = self._extract_price(section)
            
            # Link do produto
            product_link = ""
            link_element = section.find('a', class_='vtex-product-summary-2-x-clearLink')
            if link_element:
                product_link = self.base_url + link_element.get('href', '')
            
            # Imagem do produto
            img_element = section.find('img', class_='vtex-product-summary-2-x-image')
            image_url = img_element.get('src', '') if img_element else ""
            
            # Verificar se há desconto
            discount_info = self._extract_discount_info(section)
            
            product_data = {
                'name': name,
                'brand': brand,
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
    
    def _extract_price(self, section):
        """Extrai informações de preço do produto"""
        try:
            # Verificar se há desconto (preço com desconto)
            discount_price_container = section.find('div', class_='sjdigital-custom-apps-7-x-shelfPricesContainer')
            
            if discount_price_container:
                # Verificar se há preço de lista (original)
                list_price_elem = discount_price_container.find('span', class_='sjdigital-custom-apps-7-x-listPriceValue')
                selling_price_elem = discount_price_container.find('span', class_='sjdigital-custom-apps-7-x-sellingPriceValue')
                
                if list_price_elem and selling_price_elem:
                    # Produto com desconto
                    original_price = self._extract_price_value(list_price_elem)
                    current_price = self._extract_price_value(selling_price_elem)
                    
                    return {
                        'current_price': current_price,
                        'original_price': original_price
                    }
                elif selling_price_elem:
                    # Produto sem desconto
                    price = self._extract_price_value(selling_price_elem)
                    
                    return {
                        'current_price': price,
                        'original_price': price
                    }
            
            # Fallback: procurar por qualquer elemento de preço
            price_elem = section.find('span', class_='sjdigital-custom-apps-7-x-sellingPriceValue')
            if price_elem:
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
        
        # Para o São João, o preço está dividido em partes
        currency_code = price_element.find('span', class_='sjdigital-custom-apps-7-x-currencyCode')
        currency_integer = price_element.find('span', class_='sjdigital-custom-apps-7-x-currencyInteger')
        currency_decimal = price_element.find('span', class_='sjdigital-custom-apps-7-x-currencyDecimal')
        currency_fraction = price_element.find('span', class_='sjdigital-custom-apps-7-x-currencyFraction')
        
        if currency_integer:
            integer_part = currency_integer.get_text(strip=True)
            decimal_part = currency_fraction.get_text(strip=True) if currency_fraction else "00"
            
            try:
                price_str = f"{integer_part}.{decimal_part}"
                return float(price_str)
            except ValueError:
                return f"R$ {integer_part},{decimal_part}"
        
        # Fallback: tentar extrair do texto completo
        price_text = price_element.get_text(strip=True)
        price_match = re.search(r'R\$\s*([\d,]+)', price_text)
        if price_match:
            price_str = price_match.group(1).replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                return price_text
        return price_text
    
    def _extract_discount_info(self, section):
        """Extrai informações de desconto do produto"""
        try:
            # Verificar se há tag de desconto
            discount_tag = section.find('span', class_='vtex-product-price-1-x-savingsPercentage')
            
            if discount_tag:
                discount_text = discount_tag.get_text(strip=True)
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