import re
import logging
import datetime
from .base_scraper import BaseScraper
from utils.product_unifier import ProductUnifier
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                product = self._extract_product_info(article, idx, search_term, skip_open=True)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Erro ao extrair produto: {e}")
                continue
        # Paralelizar abertura das páginas específicas
        def fetch_brand_and_price_with_own_driver(product):
            import datetime
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
                now = datetime.datetime.now().strftime('%H:%M:%S')
                logger.info(f"[DrogaRaiaScraper] [{now}] (PARALLEL) Abrindo página do produto para buscar: {', '.join(reason_open)} | URL: {product_url}")
                driver.get(product_url)
                import time
                time.sleep(2)
                # Marca
                brand = None
                li_tags = []
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    li_tags = soup.find_all('li')
                except Exception:
                    pass
                for li in li_tags:
                    spans = li.find_all('span')
                    if len(spans) >= 2:
                        label = spans[0].get_text(strip=True).lower()
                        if 'fabricante' in label:
                            value_span = spans[1]
                            a_tag = value_span.find('a')
                            if a_tag and a_tag.get_text(strip=True):
                                brand = a_tag.get_text(strip=True)
                            else:
                                value_text = value_span.get_text(strip=True)
                                if value_text:
                                    brand = value_text
                            break
                if not brand:
                    for li in li_tags:
                        spans = li.find_all('span')
                        if len(spans) >= 2:
                            label = spans[0].get_text(strip=True).lower()
                            if 'marca' in label:
                                value_span = spans[1]
                                a_tag = value_span.find('a')
                                if a_tag and a_tag.get_text(strip=True):
                                    brand = a_tag.get_text(strip=True)
                                else:
                                    value_text = value_span.get_text(strip=True)
                                    if value_text:
                                        brand = value_text
                                break
                # Preço
                price = product.get('price', 'Preço não disponível')
                original_price = product.get('original_price', 'Preço não disponível')
                discount_percentage = product.get('discount_percentage', 0)
                has_discount = product.get('has_discount', False)
                try:
                    # Preço atual
                    price_span = soup.find('span', class_='sc-fd6fe09f-0 jRRyrf price-pdp-content')
                    if not price_span:
                        price_span = soup.find('span', string=lambda t: t and 'R$' in t)
                    if price_span:
                        price_text = price_span.get_text(strip=True)
                        price_match = re.search(r'R\$[\s]*([\d,.]+)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                            original_price = float(price_match.group(1).replace('.', '').replace(',', '.'))
                except Exception:
                    pass
                try:
                    # Preço original
                    original_price_span = soup.find('span', class_='sc-14e14dc8-0 kpLpXu')
                    if not original_price_span:
                        all_spans = soup.find_all('span', string=lambda t: t and 'R$' in t)
                        for span in all_spans:
                            if price_span and span == price_span:
                                continue
                            original_price_span = span
                            break
                    if original_price_span:
                        original_price_text = original_price_span.get_text(strip=True)
                        original_price_match = re.search(r'R\$[\s]*([\d,.]+)', original_price_text)
                        if original_price_match:
                            original_price = float(original_price_match.group(1).replace('.', '').replace(',', '.'))
                except Exception:
                    pass
                try:
                    # Desconto
                    discount_span = soup.find('span', class_='sc-311eb643-0 igSiSz')
                    if discount_span:
                        discount_text = discount_span.get_text(strip=True)
                        discount_match = re.search(r'(\d+)%', discount_text)
                        if discount_match:
                            discount_percentage = int(discount_match.group(1))
                            has_discount = True
                except Exception:
                    pass
                now2 = datetime.datetime.now().strftime('%H:%M:%S')
                logger.info(f"[DrogaRaiaScraper] [{now2}] (PARALLEL) Resultado da extração na página do produto: marca='{brand}', preço={{'current_price': {price}, 'original_price': {original_price}}}, desconto={{'has_discount': {has_discount}, 'percentage': {discount_percentage}}}")
                return (product_url, brand, price, original_price, discount_percentage, has_discount)
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
                        # Garantir que brand nunca seja string vazia
                        if not p['brand'] or not str(p['brand']).strip():
                            p['brand'] = "Marca não disponível"
        # Filtrar produtos com '+' no nome que não correspondem ao termo de busca
        def is_valid_plus_product(product, search_term):
            name = product.get('name', '').lower()
            search = search_term.lower()
            if '+' in name:
                after_plus = name.split('+', 1)[1]
                # Pega só as palavras (remove pontuação)
                import re
                words = re.findall(r'\b\w+\b', after_plus)
                for word in words:
                    if word not in search:
                        return False
            return True
        products = [p for p in products if is_valid_plus_product(p, search_term)]
        return products

    def _extract_product_info(self, article, position=None, search_term=None, skip_open=False):
        """
        Extrai informações de um produto do HTML
        """
        try:
            # Verificar se o produto tem "Consultar disponibilidade" - se sim, excluir
            availability_span = article.find('span', class_='sc-ddb3b127-0 RTDNF')
            if availability_span and 'Consultar disponibilidade' in availability_span.get_text(strip=True):
                self.logger.info(f"[DrogaRaiaScraper] Produto excluído - 'Consultar disponibilidade' encontrado")
                return None
            
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
            need_open_product_page = False
            reason_open = []
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
                    need_open_product_page = True
                    reason_open.append('marca')
                else:
                    final_brand = found_lab_name or brand
            # Se faltar preço, também precisa abrir a página
            if ((price_info['current_price'] == 'Preço não disponível' or price_info['original_price'] == 'Preço não disponível') and product_link):
                need_open_product_page = True
                reason_open.append('preço')
            # Se precisar abrir a página do produto, extrair marca e preço juntos
            if need_open_product_page and product_link:
                now = datetime.datetime.now().strftime('%H:%M:%S')
                self.logger.info(f"[DrogaRaiaScraper] [{now}] Abrindo página do produto para buscar: {', '.join(reason_open)} | URL: {product_link}")
                extracted_brand, extracted_price_info, extracted_discount_info = self._extract_brand_and_price_from_product_page(product_link)
                now2 = datetime.datetime.now().strftime('%H:%M:%S')
                self.logger.info(f"[DrogaRaiaScraper] [{now2}] Resultado da extração na página do produto: marca='{extracted_brand}', preço={extracted_price_info}, desconto={extracted_discount_info}")
                final_brand = extracted_brand if extracted_brand else final_brand
                if extracted_price_info:
                    price_info = extracted_price_info
                if extracted_discount_info:
                    discount_info = extracted_discount_info
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
            self.logger.info(f"[DrogaRaiaScraper] Produto final: {product_data}")
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

    def _extract_brand_and_price_from_product_page(self, product_url):
        """
        Acessa a página do produto e extrai marca, preço e desconto juntos.
        """
        try:
            if not product_url:
                return None, None, None
            response = self.make_request(product_url)
            soup = self.parse_html(response['content'])
            # Marca
            brand = None
            li_tags = soup.find_all('li')
            for li in li_tags:
                spans = li.find_all('span')
                if len(spans) >= 2:
                    label = spans[0].get_text(strip=True).lower()
                    if 'fabricante' in label:
                        value_span = spans[1]
                        a_tag = value_span.find('a')
                        if a_tag and a_tag.get_text(strip=True):
                            brand = a_tag.get_text(strip=True)
                        else:
                            value_text = value_span.get_text(strip=True)
                            if value_text:
                                brand = value_text
                        break
            if not brand:
                for li in li_tags:
                    spans = li.find_all('span')
                    if len(spans) >= 2:
                        label = spans[0].get_text(strip=True).lower()
                        if 'marca' in label:
                            value_span = spans[1]
                            a_tag = value_span.find('a')
                            if a_tag and a_tag.get_text(strip=True):
                                brand = a_tag.get_text(strip=True)
                            else:
                                value_text = value_span.get_text(strip=True)
                                if value_text:
                                    brand = value_text
                            break
            # Preço
            price_info = {'current_price': 'Preço não disponível', 'original_price': 'Preço não disponível'}
            discount_info = {'has_discount': False, 'percentage': 0}
            # Preço atual
            price_span = soup.find('span', class_='sc-fd6fe09f-0 jRRyrf price-pdp-content')
            if not price_span:
                price_span = soup.find('span', string=lambda t: t and 'R$' in t)
            if price_span:
                price_text = price_span.get_text(strip=True)
                price_match = re.search(r'R\$[\s]*([\d,.]+)', price_text)
                if price_match:
                    price_info['current_price'] = float(price_match.group(1).replace('.', '').replace(',', '.'))
                    price_info['original_price'] = float(price_match.group(1).replace('.', '').replace(',', '.'))
            # Preço original
            original_price_span = soup.find('span', class_='sc-14e14dc8-0 kpLpXu')
            if not original_price_span:
                all_spans = soup.find_all('span', string=lambda t: t and 'R$' in t)
                for span in all_spans:
                    if price_span and span == price_span:
                        continue
                    original_price_span = span
                    break
            if original_price_span:
                original_price_text = original_price_span.get_text(strip=True)
                original_price_match = re.search(r'R\$[\s]*([\d,.]+)', original_price_text)
                if original_price_match:
                    price_info['original_price'] = float(original_price_match.group(1).replace('.', '').replace(',', '.'))
            # Desconto
            discount_span = soup.find('span', class_='sc-311eb643-0 igSiSz')
            if discount_span:
                discount_text = discount_span.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    discount_info['percentage'] = int(discount_match.group(1))
                    discount_info['has_discount'] = True
            # Fallback robusto: todos os <span> com 'R$'
            if (price_info['current_price'] == 'Preço não disponível' or price_info['original_price'] == 'Preço não disponível'):
                all_price_spans = soup.find_all('span', string=lambda t: t and 'R$' in t)
                prices_found = []
                for span in all_price_spans:
                    price_text = span.get_text(strip=True)
                    price_match = re.search(r'R\$[\s]*([\d,.]+)', price_text)
                    if price_match:
                        value = float(price_match.group(1).replace('.', '').replace(',', '.'))
                        prices_found.append(value)
                if prices_found:
                    if len(prices_found) >= 2:
                        price_info['original_price'] = max(prices_found)
                        price_info['current_price'] = min(prices_found)
                    else:
                        price_info['current_price'] = prices_found[0]
                        price_info['original_price'] = prices_found[0]
                    self.logger.info(f"[DrogaRaiaScraper] Preços encontrados na página do produto: {prices_found}")
            return brand, price_info, discount_info
        except Exception as e:
            self.logger.error(f"Erro ao extrair marca/preço da página do produto: {e}")
            return None, None, None 