from abc import ABC, abstractmethod
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import os
import platform
import requests
import zipfile

class BaseScraper(ABC):
    """Classe base para todos os scrapers de farmácias usando Selenium"""
    
    def __init__(self, base_url, search_url, pharmacy_name, driver=None):
        """
        Inicializa o scraper base
        
        Args:
            base_url (str): URL base da farmácia
            search_url (str): URL de busca da farmácia
            pharmacy_name (str): Nome da farmácia
            driver (webdriver, optional): Driver Selenium externo para reutilização
        """
        self.base_url = base_url
        self.search_url = search_url
        self.pharmacy_name = pharmacy_name
        self.driver = driver
        self.logger = logging.getLogger(self.__class__.__name__)
        self._owns_driver = driver is None  # Indica se este scraper é responsável por limpar o driver
    
    def _setup_driver(self):
        """Configura o driver do Chrome com opções para evitar detecção"""
        if self.driver is not None:
            self.logger.info("Driver já configurado, reutilizando...")
            return
            
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless=new")  # Executa o Chrome de forma oculta
        chrome_options.add_argument("--window-size=1920,1080")
        # Inicializar o driver
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.warning(f"Erro ao baixar ChromeDriver automaticamente: {e}")
            self.logger.info("Tentando usar ChromeDriver local...")
            try:
                # Tentar usar ChromeDriver local
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                self.logger.error(f"Erro ao inicializar ChromeDriver: {e2}")
                raise Exception(f"Não foi possível inicializar o ChromeDriver: {e2}")
        # Executar script para remover propriedades de automação
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.logger.info("Driver do Chrome configurado com sucesso")
    
    @abstractmethod
    def search(self, medicine_description):
        """
        Busca medicamentos na farmácia
        
        Args:
            medicine_description (str): Descrição do medicamento
            
        Returns:
            dict: Resultados da busca
        """
        pass
    
    @abstractmethod
    def _extract_products(self, soup):
        """
        Extrai produtos do HTML parseado
        
        Args:
            soup (BeautifulSoup): HTML parseado
            
        Returns:
            list: Lista de produtos extraídos
        """
        pass
    
    @abstractmethod
    def _extract_product_info(self, product_element):
        """
        Extrai informações de um produto específico
        
        Args:
            product_element: Elemento HTML do produto
            
        Returns:
            dict: Informações do produto
        """
        pass
    
    def make_request(self, url, timeout=30):
        """
        Faz uma requisição HTTP usando Selenium
        
        Args:
            url (str): URL para fazer a requisição
            timeout (int): Timeout em segundos
            
        Returns:
            dict: Dados da página carregada
        """
        try:
            # Configurar driver se necessário
            if not self.driver:
                self._setup_driver()
            
            # Navegar para a página
            self.driver.get(url)
            self.logger.info("Página carregada")
            
            # Aguardar carregamento da página
            time.sleep(3)
            
            # Aguardar pelo container de produtos
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="container-products"]'))
                )
                self.logger.info("Container de produtos encontrado")
            except Exception as e:
                self.logger.warning(f"Container de produtos não encontrado: {e}")
                # Tentar aguardar mais um pouco
                time.sleep(5)
            
            # Obter o HTML da página
            page_source = self.driver.page_source
            self.logger.debug(f"Tamanho do HTML: {len(page_source)} caracteres")
            
            return {
                'content': page_source,
                'status_code': 200,
                'url': url
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar {url}: {str(e)}")
            raise Exception(f"Erro ao acessar {url}: {str(e)}")
    
    def parse_html(self, content):
        """
        Parseia o conteúdo HTML
        
        Args:
            content (str): Conteúdo HTML
            
        Returns:
            BeautifulSoup: HTML parseado
        """
        return BeautifulSoup(content, 'html.parser')
    
    def create_search_url(self, medicine_description):
        """
        Cria a URL de busca baseada na descrição do medicamento
        
        Args:
            medicine_description (str): Descrição do medicamento
            
        Returns:
            str: URL de busca
        """
        search_query = quote_plus(medicine_description)
        return f"{self.search_url}?w={search_query}"
    
    def format_response(self, products, url, error=None):
        """
        Formata a resposta padrão do scraper
        
        Args:
            products (list): Lista de produtos
            url (str): URL da busca
            error (str, optional): Mensagem de erro
            
        Returns:
            dict: Resposta formatada
        """
        if error:
            return {
                'pharmacy': self.pharmacy_name,
                'error': error,
                'products': [],
                'url': url,
                'total_products': 0
            }
        
        return {
            'pharmacy': self.pharmacy_name,
            'url': url,
            'products': products,
            'total_products': len(products)
        }
    
    def cleanup(self):
        """Limpa recursos do driver apenas se for o proprietário"""
        if self.driver and self._owns_driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Driver encerrado pelo scraper")

# ChromeDriver Management

def get_chrome_version():
    """Retrieve the installed version of Google Chrome."""
    try:
        return os.popen(
            r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
        ).read().split()[-1]
    except Exception:
        raise RuntimeError("Unable to retrieve Chrome version.")

def get_chromedriver_url(version):
    """Get the download URL for the corresponding ChromeDriver version."""
    major_version = version.split('.')[0]
    response = requests.get(
        "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json",
        verify=False
    )
    if response.status_code == 200:
        data = response.json()
        for entry in data["versions"]:
            if entry["version"].startswith(major_version):
                os_type = get_os_type()
                for download in entry["downloads"]["chromedriver"]:
                    if download["platform"] == os_type:
                        return download["url"]
    raise RuntimeError(f"Unable to find ChromeDriver for version {version}.")

def update_chromedriver(url):
    """Download and update ChromeDriver."""
    CHROMEDRIVER_DIR = os.path.join(os.getcwd(), "chromedriver_bin")
    os.makedirs(CHROMEDRIVER_DIR, exist_ok=True)
    zip_path = os.path.join(CHROMEDRIVER_DIR, "chromedriver.zip")
    response = requests.get(url, stream=True)
    try:
        if response.status_code == 200:
            with open(zip_path, "wb") as file:
                file.write(response.content)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(CHROMEDRIVER_DIR)
            os.remove(zip_path)
            print("ChromeDriver successfully updated.")
        else:
            raise RuntimeError("Failed to download ChromeDriver.")
    except Exception as e:
        print(f"Failed to update ChromeDriver: {e}")

def get_os_type():
    """Identify the OS type for ChromeDriver compatibility."""
    system = platform.system().lower()
    return {"windows": "win64", "linux": "linux64", "darwin": "mac64"}.get(system, None) 