import re
import logging
import datetime
from .base_scraper import BaseScraper
from utils.product_unifier import ProductUnifier
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("PanvelScraper")

class PanvelScraper(BaseScraper):
    """Scraper para o site Panvel usando Selenium"""
    
    def __init__(self, driver=None):
        super().__init__(
            base_url="https://www.panvel.com/panvel",
            search_url="https://www.panvel.com/panvel/buscarProduto.do",
            pharmacy_name="Panvel",
            driver=driver
        )
        self.product_unifier = ProductUnifier()  # Instância única

    def create_search_url(self, medicine_description):
        # Panvel usa termoPesquisa na query
        from urllib.parse import quote_plus
        search_query = quote_plus(medicine_description)
        return f"{self.search_url}?termoPesquisa={search_query}"

    def search(self, medicine_description):
        """
        Busca medicamentos no site Panvel
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
        # Panvel: produtos estão em <lib-card-item-v2-vertical> e <lib-card-item-v2-horizontal>
        products = []
        product_cards = soup.find_all(['lib-card-item-v2-vertical', 'lib-card-item-v2-horizontal'])
        self.logger.info(f"Quantidade de cards de produtos encontrados: {len(product_cards)}")
        for idx, card in enumerate(product_cards, 1):
            try:
                product = self._extract_product_info(card, idx, search_term)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        # Paralelizar abertura das páginas específicas para marca/preço
        def fetch_brand_and_price_with_own_driver(product):
            product_url = product.get('product_url')
            reason_open = []
            if product.get('brand') in [None, '', 'Marca não disponível']:
                reason_open.append('marca')
            if product.get('price') == 'Preço não disponível' or product.get('original_price') == 'Preço não disponível':
                reason_open.append('preço')
            if not product_url:
                return (product_url, product.get('brand'), product.get('price'), product.get('original_price'), product.get('discount_percentage'), product.get('has_discount'))
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
                driver.get(product_url)
                import time
                time.sleep(2)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # Marca
                brand = None
                brand_span = soup.find('span', class_='brand-name')
                if brand_span:
                    brand = brand_span.get_text(strip=True)
                # Preço
                price_info = self._extract_price_from_product_page(soup)
                # Desconto
                discount_info = self._extract_discount_info_from_product_page(soup)
                return (product_url, brand, price_info['current_price'], price_info['original_price'], discount_info['percentage'], discount_info['has_discount'])
            finally:
                driver.quit()
        # Coletar produtos que precisam buscar marca ou preço
        products_to_update = [p for p in products if (p.get('brand') in [None, '', 'Marca não disponível'] or p.get('price') == 'Preço não disponível' or p.get('original_price') == 'Preço não disponível') and p.get('product_url')]
        if products_to_update:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {executor.submit(fetch_brand_and_price_with_own_driver, p): p for p in products_to_update}
                url_to_data = {}
                for future in as_completed(future_to_url):
                    url, brand, price, original_price, discount_percentage, has_discount = future.result()
                    # Capitalizar brand, exceto EMS
                    if isinstance(brand, str) and brand.strip():
                        if brand.strip().upper() == 'EMS':
                            brand = 'EMS'
                        else:
                            brand = ' '.join([w.capitalize() for w in brand.strip().split()])
                    url_to_data[url] = (brand, price, original_price, discount_percentage, has_discount)
                # Atualizar produtos
                for p in products:
                    if p.get('product_url') in url_to_data:
                        brand, price, original_price, discount_percentage, has_discount = url_to_data[p['product_url']]
                        p['brand'] = brand
                        p['price'] = price
                        p['original_price'] = original_price
                        p['discount_percentage'] = discount_percentage
                        p['has_discount'] = has_discount
                        if not p['brand'] or not str(p['brand']).strip():
                            p['brand'] = "Marca não disponível"
        # Filtro '+'
        import unicodedata
        def normalize(text):
            return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()
        def is_valid_plus_product(product, search_term):
            name = normalize(product.get('name', ''))
            search = normalize(search_term)
            if '+' in name:
                after_plus = name.split('+', 1)[1]
                import re
                words = re.findall(r'\b\w+\b', after_plus)
                for word in words:
                    if word not in search:
                        logger.info(f"[PanvelScraper] Produto eliminado pelo filtro '+': '{product.get('name', '')}' (palavra '{word}' não está na busca '{search_term}')")
                        return False
            return True
        products = [p for p in products if is_valid_plus_product(p, search_term)]
        return products

    def _extract_product_info(self, card, position=None, search_term=None):
        """
        Extrai informações de um produto do HTML
        """
        try:
            # Nome do produto
            name_element = card.find('span', class_='item-name')
            name = name_element.get_text(strip=True) if name_element else "Nome não disponível"
            # Marca
            brand_element = card.find('span', class_='brand-name')
            brand = brand_element.get_text(strip=True) if brand_element else "Marca não disponível"
            # Descrição/Quantidade
            desc_element = card.find('div', class_='presentation-title')
            description = desc_element.get_text(strip=True) if desc_element else ""
            # Preço
            price_info = self._extract_price(card)
            # Link do produto
            link_element = card.find('a', href=True)
            product_link = link_element['href'] if link_element else ""
            if product_link and not product_link.startswith('http'):
                product_link = self.base_url + product_link
            # Imagem
            img_element = card.find('img', class_='item-image')
            image_url = img_element.get('src', '') if img_element else ""
            # Desconto
            discount_info = self._extract_discount_info(card)
            # --- Lógica de normalização de marca ---
            final_brand = brand
            if name and search_term:
                found_lab = self.product_unifier.find_best_match(
                    product_name=name,
                    product_brand=brand,
                    product_description=description,
                    search_term=search_term
                )
                found_lab_name = found_lab['laboratory'] if found_lab and found_lab.get('laboratory') else ""
                if found_lab_name:
                    final_brand = found_lab_name
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
            self.logger.info(f"[PanvelScraper] Produto final: {product_data}")
            return product_data
        except Exception as e:
            self.logger.error(f"Erro ao extrair informações do produto: {e}")
            return None

    def _extract_price(self, card):
        """Extrai informações de preço do produto"""
        try:
            # Preço principal
            price_span = card.find('span', class_='price')
            if price_span:
                price_text = price_span.get_text(strip=True)
                price_match = re.search(r'R\$\s*([\d,.]+)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                    return {'current_price': price, 'original_price': price}
            # Preço especial (ex: 2 por R$ X,XX cada)
            special_price_span = card.find('span', class_='price special')
            if special_price_span:
                price_text = special_price_span.get_text(strip=True)
                price_match = re.search(r'R\$\s*([\d,.]+)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                    return {'current_price': price, 'original_price': price}
            return {'current_price': "Preço não disponível", 'original_price': "Preço não disponível"}
        except Exception as e:
            self.logger.error(f"Erro ao extrair preço: {e}")
            return {'current_price': "Preço não disponível", 'original_price': "Preço não disponível"}

    def _extract_discount_info(self, card):
        """Extrai informações de desconto do produto"""
        try:
            discount_span = card.find('span', class_='discount-percentage')
            if discount_span:
                discount_text = discount_span.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    return {'has_discount': True, 'percentage': int(discount_match.group(1))}
            return {'has_discount': False, 'percentage': 0}
        except Exception as e:
            self.logger.error(f"Erro ao extrair desconto: {e}")
            return {'has_discount': False, 'percentage': 0}

    def _extract_price_from_product_page(self, soup):
        """Extrai preço da página do produto"""
        try:
            price_span = soup.find('span', class_='deal-price')
            if price_span:
                price_text = price_span.get_text(strip=True)
                price_match = re.search(r'R\$\s*([\d,.]+)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                    return {'current_price': price, 'original_price': price}
            original_price_span = soup.find('span', class_='original-price')
            if original_price_span:
                original_price_text = original_price_span.get_text(strip=True)
                original_price_match = re.search(r'R\$\s*([\d,.]+)', original_price_text)
                if original_price_match:
                    original_price = float(original_price_match.group(1).replace('.', '').replace(',', '.'))
                    return {'current_price': original_price, 'original_price': original_price}
            return {'current_price': "Preço não disponível", 'original_price': "Preço não disponível"}
        except Exception as e:
            self.logger.error(f"Erro ao extrair preço da página do produto: {e}")
            return {'current_price': "Preço não disponível", 'original_price': "Preço não disponível"}

    def _extract_discount_info_from_product_page(self, soup):
        """Extrai desconto da página do produto"""
        try:
            discount_span = soup.find('span', {'data-cy': 'product-discount'})
            if discount_span:
                discount_text = discount_span.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    return {'has_discount': True, 'percentage': int(discount_match.group(1))}
            return {'has_discount': False, 'percentage': 0}
        except Exception as e:
            self.logger.error(f"Erro ao extrair desconto da página do produto: {e}")
            return {'has_discount': False, 'percentage': 0} 