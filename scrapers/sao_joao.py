import re
import logging
import time
from .base_scraper import BaseScraper
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.product_unifier import ProductUnifier
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        self.product_unifier = ProductUnifier()  # Instância única

    def search(self, medicine_description):
        """
        Busca medicamentos no site São João
        """
        try:
            url = self.create_search_url(medicine_description)
            self.logger.info(f"Buscando URL: {url}")
            response = self.make_request(url)
            soup = self.parse_html(response)
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
    
    def _extract_products(self, soup, search_term):
        """
        Extrai produtos do HTML parseado
        """
        products_container = soup.find('div', class_='vtex-search-result-3-x-gallery')
        if not products_container:
            self.logger.warning("Container de produtos não encontrado no HTML.")
            self.logger.debug(f"HTML da página (primeiros 1000 chars):\n{str(soup)[:1000]}")
            return []
        products = []
        product_sections = products_container.find_all('section', class_='vtex-product-summary-2-x-container')
        self.logger.info(f"Quantidade de seções de produtos encontradas: {len(product_sections)}")
        for idx, section in enumerate(product_sections, 1):
            try:
                product = self._extract_product_info(section, idx, search_term)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        # Paralelizar busca de marca nas páginas específicas
        def fetch_brand_with_own_driver(product):
            product_url = product.get('product_url')
            if not product_url:
                return (product_url, product.get('brand'))
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            import platform
            import os
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            CHROMEDRIVER_DIR = os.path.join(os.getcwd(), "chromedriver_bin")
            chromedriver_path = os.path.join(CHROMEDRIVER_DIR, "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
            if not os.path.exists(chromedriver_path):
                chromedriver_path_alt = os.path.join(CHROMEDRIVER_DIR, "chromedriver-win64", "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
                if os.path.exists(chromedriver_path_alt):
                    chromedriver_path = chromedriver_path_alt
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            try:
                # Lógica de _extract_brand_from_product_page, mas com driver local
                driver.get(product_url)
                import time
                time.sleep(2)
                # Tentar aceitar cookies se o botão existir
                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(translate(., 'ACEITAR', 'aceitar'), 'aceitar') or contains(., 'Aceitar') or contains(., 'OK') or contains(., 'Ok') or contains(., 'ok') or contains(., 'Concordo') or contains(., 'concordo')]")
                        )
                    ).click()
                except Exception:
                    pass
                time.sleep(1)
                # Buscar marca usando os seletores já existentes
                brand = None
                try:
                    brand_selectors = [
                        "span.vtex-store-components-3-x-productBrandName",
                        ".vtex-store-components-3-x-productBrandName",
                        "span[class*='productBrandName']",
                        ".vtex-product-identifier-0-x-product-identifier__value",
                        "span[class*='brand']",
                        ".vtex-product-identifier-0-x-product-identifier__value",
                        "span[class*='manufacturer']",
                        ".vtex-product-identifier-0-x-product-identifier__value",
                        "[class*='brand']",
                        "[class*='manufacturer']",
                        "[class*='productBrand']"
                    ]
                    for selector in brand_selectors:
                        try:
                            brand_element = driver.find_element(By.CSS_SELECTOR, selector)
                            brand_text = brand_element.text.strip()
                            if brand_text and len(brand_text) > 1:
                                return (product_url, brand_text)
                        except Exception:
                            continue
                except Exception:
                    pass
                # Se não encontrar, tentar extrair do título
                try:
                    page_title = driver.title
                    if page_title:
                        import re
                        brand_match = re.search(r'^([^-]+)', page_title)
                        if brand_match:
                            brand_text = brand_match.group(1).strip()
                            if brand_text and len(brand_text) > 2:
                                return (product_url, brand_text)
                except Exception:
                    pass
                return (product_url, "Marca não disponível")
            finally:
                driver.quit()
        # Coletar produtos que precisam buscar marca
        products_to_update = [p for p in products if p.get('brand') in [None, '', 'Marca não disponível'] and p.get('product_url')]
        if products_to_update:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_url = {executor.submit(fetch_brand_with_own_driver, p): p for p in products_to_update}
                url_to_brand = {}
                for future in as_completed(future_to_url):
                    url, brand = future.result()
                    # Capitalizar brand, exceto EMS
                    if isinstance(brand, str) and brand.strip():
                        if brand.strip().upper() == 'EMS':
                            brand = 'EMS'
                        else:
                            brand = ' '.join([w.capitalize() for w in brand.strip().split()])
                    url_to_brand[url] = brand
                # Atualizar produtos
                for p in products:
                    if p.get('product_url') in url_to_brand:
                        p['brand'] = url_to_brand[p['product_url']]
                        # Garantir que brand nunca seja string vazia
                        if not p['brand'] or not str(p['brand']).strip():
                            p['brand'] = "Marca não disponível"
        return products

    def _extract_product_info(self, section, position=None, search_term=None):
        """
        Extrai informações de um produto do HTML
        """
        try:
            # Nome do produto
            name_element = section.find('span', class_='vtex-product-summary-2-x-productBrand')
            name = name_element.get_text(strip=True) if name_element else "Nome não disponível"
            # Link do produto
            product_link = ""
            link_element = section.find('a', class_='vtex-product-summary-2-x-clearLink')
            if link_element:
                product_link = self.base_url + link_element.get('href', '')
            # Descrição/Quantidade - extrair do nome
            description = ""
            if name:
                desc_match = re.search(r'(\d+mg?\s+\d+\s+\w+)', name)
                if desc_match:
                    description = desc_match.group(1)
            # Preço
            price_info = self._extract_price(section)
            # Imagem do produto
            img_element = section.find('img', class_='vtex-product-summary-2-x-image')
            image_url = img_element.get('src', '') if img_element else ""
            # Verificar se há desconto
            discount_info = self._extract_discount_info(section)
            # --- Lógica de busca da marca ---
            brand = None
            
            # Primeiro, tentar usar o ProductUnifier
            if name and search_term:
                found_lab = self.product_unifier.find_best_match(
                    product_name=name,
                    product_brand="",
                    product_description=description,
                    search_term=search_term
                )
                if found_lab and found_lab.get('laboratory'):
                    brand = found_lab['laboratory']
            
            # Se não encontrou com ProductUnifier, buscar na página específica
            if not brand and product_link:
                brand = self._extract_brand_from_product_page(product_link)
            
            # Se ainda não encontrou, usar "Marca não disponível"
            if not brand:
                brand = "Marca não disponível"
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
            # Capitalizar brand, exceto EMS
            brand_value = product_data.get('brand', '')
            if isinstance(brand_value, str) and brand_value.strip():
                if brand_value.strip().upper() == 'EMS':
                    brand_value = 'EMS'
                else:
                    brand_value = ' '.join([w.capitalize() for w in brand_value.strip().split()])
            product_data['brand'] = brand_value

            # Logar valor final de brand
            self.logger.info(f"[DEBUG] Valor final de brand para '{name}': '{product_data['brand']}'")

            # Garantir que brand nunca seja string vazia
            if not product_data['brand'] or not str(product_data['brand']).strip():
                product_data['brand'] = "Marca não disponível"

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
    
    def _extract_brand_from_product_page(self, product_url):
        """
        Extrai a marca correta da página do produto
        """
        if not product_url:
            return "Marca não disponível"
        tried_restart = False
        while True:
            try:
                self.logger.info(f"Acessando página do produto: {product_url}")
                self.driver.get(product_url)
                time.sleep(2)
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(translate(., 'ACEITAR', 'aceitar'), 'aceitar') or contains(., 'Aceitar') or contains(., 'OK') or contains(., 'Ok') or contains(., 'ok') or contains(., 'Concordo') or contains(., 'concordo')]")
                        )
                    ).click()
                    self.logger.info("Cookies aceitos na página do produto")
                except Exception:
                    pass
                time.sleep(1)
                brand = self._find_brand_in_page()
                if brand and brand != "Marca não disponível":
                    self.logger.info(f"Marca encontrada: {brand}")
                    return brand
                else:
                    self.logger.warning("Marca não encontrada na página do produto")
                    return "Marca não disponível"
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Erro ao acessar página do produto: {e}")
                if (not tried_restart) and ('invalid session id' in error_msg.lower()):
                    from app import cleanup_global_driver, setup_global_driver, get_global_driver
                    cleanup_global_driver()
                    setup_global_driver()
                    self.driver = get_global_driver()
                    tried_restart = True
                    continue
                return "Marca não disponível"
    
    def _find_brand_in_page(self):
        """
        Procura pela marca na página do produto usando diferentes seletores
        
        Returns:
            str: Nome da marca encontrada ou "Marca não disponível"
        """
        try:
            # Lista de seletores para tentar encontrar a marca
            brand_selectors = [
                "span.vtex-store-components-3-x-productBrandName",
                ".vtex-store-components-3-x-productBrandName",
                "span[class*='productBrandName']",
                ".vtex-product-identifier-0-x-product-identifier__value",
                "span[class*='brand']",
                ".vtex-product-identifier-0-x-product-identifier__value",
                "span[class*='manufacturer']",
                ".vtex-product-identifier-0-x-product-identifier__value",
                # Adicionar mais seletores genéricos
                "[class*='brand']",
                "[class*='manufacturer']",
                "[class*='productBrand']"
            ]
            
            for selector in brand_selectors:
                try:
                    brand_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    brand_text = brand_element.text.strip()
                    if brand_text and len(brand_text) > 1:
                        self.logger.info(f"Marca encontrada com seletor '{selector}': {brand_text}")
                        return brand_text
                except Exception as e:
                    self.logger.debug(f"Seletor '{selector}' não encontrado: {e}")
                    continue
            
            # Tentar com XPath também
            xpath_selectors = [
                "//span[contains(@class, 'productBrandName')]",
                "//span[contains(@class, 'brand')]",
                "//span[contains(@class, 'manufacturer')]",
                "//div[contains(@class, 'productBrandName')]",
                "//div[contains(@class, 'brand')]",
                "//*[contains(@class, 'brand')]",
                "//*[contains(@class, 'manufacturer')]"
            ]
            
            for xpath in xpath_selectors:
                try:
                    brand_element = self.driver.find_element(By.XPATH, xpath)
                    brand_text = brand_element.text.strip()
                    if brand_text and len(brand_text) > 1:
                        self.logger.info(f"Marca encontrada com XPath '{xpath}': {brand_text}")
                        return brand_text
                except Exception as e:
                    self.logger.debug(f"XPath '{xpath}' não encontrado: {e}")
                    continue
            
            # Se não encontrar com seletores específicos, tentar extrair do título da página
            try:
                page_title = self.driver.title
                if page_title:
                    # Tentar extrair marca do título
                    brand_match = re.search(r'^([^-]+)', page_title)
                    if brand_match:
                        brand_text = brand_match.group(1).strip()
                        if brand_text and len(brand_text) > 2:
                            self.logger.info(f"Marca extraída do título: {brand_text}")
                            return brand_text
            except Exception as e:
                self.logger.debug(f"Erro ao extrair marca do título: {e}")
            
            # Tentar extrair do URL da página
            try:
                current_url = self.driver.current_url
                if current_url:
                    # Tentar extrair marca do URL
                    url_parts = current_url.split('/')
                    for part in url_parts:
                        if part and len(part) > 2 and not part.startswith('http'):
                            # Verificar se parece ser uma marca
                            if not any(char.isdigit() for char in part) and part not in ['www', 'com', 'br', 'farmacias']:
                                self.logger.info(f"Marca extraída do URL: {part}")
                                return part
            except Exception as e:
                self.logger.debug(f"Erro ao extrair marca do URL: {e}")
            
            self.logger.warning("Nenhuma marca encontrada na página do produto")
            return "Marca não disponível"
            
        except Exception as e:
            self.logger.error(f"Erro ao procurar marca na página: {e}")
            return "Marca não disponível"
    
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