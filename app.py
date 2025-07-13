from flask import Flask, render_template, request, jsonify, Blueprint
from scrapers.droga_raia import DrogaRaiaScraper
from scrapers.sao_joao import SaoJoaoScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import platform

# Importar funções do base_scraper
from scrapers.base_scraper import get_chrome_version, get_chromedriver_url, update_chromedriver, get_os_type

# Importar o unificador de produtos
from utils.product_unifier import unify_pharmacy_results

# Variável global para o driver
global_driver = None

def setup_global_driver():
    """Configura o driver global do Selenium"""
    global global_driver
    
    try:
        # Verificar se o ChromeDriver está atualizado
        chrome_version = get_chrome_version()
        print(f"Versão do Chrome detectada: {chrome_version}")
        
        # Tentar obter URL do ChromeDriver
        try:
            chromedriver_url = get_chromedriver_url(chrome_version)
            print(f"URL do ChromeDriver: {chromedriver_url}")
            
            # Atualizar ChromeDriver se necessário
            CHROMEDRIVER_DIR = os.path.join(os.getcwd(), "chromedriver_bin")
            chromedriver_path = os.path.join(CHROMEDRIVER_DIR, "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
            # Se não encontrar, tente na subpasta chromedriver-win64
            if not os.path.exists(chromedriver_path):
                chromedriver_path_alt = os.path.join(CHROMEDRIVER_DIR, "chromedriver-win64", "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
                if os.path.exists(chromedriver_path_alt):
                    chromedriver_path = chromedriver_path_alt
            
            if not os.path.exists(chromedriver_path):
                print("ChromeDriver não encontrado. Baixando...")
                update_chromedriver(chromedriver_url)
            
        except Exception as e:
            print(f"Erro ao obter ChromeDriver: {e}")
            print("Usando ChromeDriverManager como fallback...")
        
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializar o driver
        try:
            # Tentar usar ChromeDriver local primeiro
            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
                global_driver = webdriver.Chrome(service=service, options=chrome_options)
                print("Driver inicializado com ChromeDriver local")
            else:
                # Fallback para ChromeDriverManager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                global_driver = webdriver.Chrome(service=service, options=chrome_options)
                print("Driver inicializado com ChromeDriverManager")
                
        except Exception as e:
            print(f"Erro ao inicializar driver: {e}")
            raise Exception(f"Não foi possível inicializar o ChromeDriver: {e}")
        
        # Executar script para remover propriedades de automação
        global_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Driver global configurado com sucesso")
        
    except Exception as e:
        print(f"Erro na configuração do driver: {e}")
        raise e

def get_global_driver():
    """Retorna o driver global"""
    global global_driver
    if global_driver is None:
        setup_global_driver()
    return global_driver

def cleanup_global_driver():
    """Limpa o driver global"""
    global global_driver
    if global_driver:
        global_driver.quit()
        global_driver = None
        print("Driver global encerrado")

# Criar blueprint para as rotas da API
pharma_api = Blueprint('pharma_api', __name__, url_prefix='/api/pharma')

@pharma_api.route('/search', methods=['POST'])
def search_medicines():
    """API endpoint para buscar medicamentos em diferentes farmácias"""
    try:
        data = request.get_json()
        medicine_description = data.get('medicine_description', '').strip()
        
        if not medicine_description:
            return jsonify({'error': 'Descrição do medicamento é obrigatória'}), 400
        
        # Obter driver global
        driver = get_global_driver()
        
        # Lista de scrapers disponíveis
        scrapers = {
            'droga_raia': DrogaRaiaScraper(driver=driver),
            'sao_joao': SaoJoaoScraper(driver=driver)
        }
        
        results = {}
        
        # Executar busca em cada farmácia
        for pharmacy_name, scraper in scrapers.items():
            tried_restart = False
            while True:
                try:
                    pharmacy_results = scraper.search(medicine_description)
                    results[pharmacy_name] = pharmacy_results
                    break
                except Exception as e:
                    error_msg = str(e)
                    if (not tried_restart) and ('invalid session id' in error_msg.lower()):
                        # Reiniciar driver global e tentar novamente uma vez
                        cleanup_global_driver()
                        setup_global_driver()
                        # Recriar o scraper específico
                        if pharmacy_name == 'droga_raia':
                            scrapers[pharmacy_name] = DrogaRaiaScraper(driver=get_global_driver())
                        elif pharmacy_name == 'sao_joao':
                            scrapers[pharmacy_name] = SaoJoaoScraper(driver=get_global_driver())
                        tried_restart = True
                        continue
                    results[pharmacy_name] = {
                        'error': f'Erro ao buscar em {pharmacy_name}: {error_msg}',
                        'products': []
                    }
                    break
        
        # Unificar produtos semelhantes
        unified_results = unify_pharmacy_results(results, similarity_threshold=0.7)
        
        return jsonify({
            'medicine_description': medicine_description,
            'results': results,
            'unified_results': unified_results
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@pharma_api.route('/search_unified', methods=['POST'])
def search_medicines_unified():
    """API endpoint para buscar medicamentos e retornar apenas resultados unificados"""
    try:
        data = request.get_json()
        medicine_description = data.get('medicine_description', '').strip()
        
        if not medicine_description:
            return jsonify({'error': 'Descrição do medicamento é obrigatória'}), 400
        
        # Obter driver global
        driver = get_global_driver()
        
        # Lista de scrapers disponíveis
        scrapers = {
            'droga_raia': DrogaRaiaScraper(driver=driver),
            'sao_joao': SaoJoaoScraper(driver=driver)
        }
        
        results = {}
        
        # Executar busca em cada farmácia
        for pharmacy_name, scraper in scrapers.items():
            tried_restart = False
            while True:
                try:
                    pharmacy_results = scraper.search(medicine_description)
                    results[pharmacy_name] = pharmacy_results
                    break
                except Exception as e:
                    error_msg = str(e)
                    if (not tried_restart) and ('invalid session id' in error_msg.lower()):
                        # Reiniciar driver global e tentar novamente uma vez
                        cleanup_global_driver()
                        setup_global_driver()
                        # Recriar o scraper específico
                        if pharmacy_name == 'droga_raia':
                            scrapers[pharmacy_name] = DrogaRaiaScraper(driver=get_global_driver())
                        elif pharmacy_name == 'sao_joao':
                            scrapers[pharmacy_name] = SaoJoaoScraper(driver=get_global_driver())
                        tried_restart = True
                        continue
                    results[pharmacy_name] = {
                        'error': f'Erro ao buscar em {pharmacy_name}: {error_msg}',
                        'products': []
                    }
                    break
        
        # Unificar produtos semelhantes
        unified_results = unify_pharmacy_results(results, similarity_threshold=0.7)
        
        return jsonify(unified_results)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@pharma_api.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o driver está funcionando"""
    try:
        driver = get_global_driver()
        # Testar se o driver está respondendo
        driver.current_url
        return jsonify({'status': 'healthy', 'driver': 'active'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Criar blueprint para as rotas da interface web
pharma_web = Blueprint('pharma_web', __name__)

@pharma_web.route('/')
def index():
    """Página principal com interface para busca de medicamentos"""
    return render_template('index.html')

# Função para criar a aplicação Flask
def create_app(config=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurar a aplicação
    if config:
        app.config.update(config)
    
    # Registrar blueprints
    app.register_blueprint(pharma_api)
    app.register_blueprint(pharma_web)
    
    # Configurar limpeza do driver ao encerrar
    import atexit
    atexit.register(cleanup_global_driver)
    
    return app

# Função para inicializar o driver global
def init_driver():
    """Inicializa o driver global"""
    try:
        setup_global_driver()
        print("Driver global inicializado com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao inicializar driver: {e}")
        return False

# Função para obter os blueprints (útil para integração)
def get_blueprints():
    """Retorna os blueprints para integração em outras aplicações"""
    return [pharma_api, pharma_web]

def main():
    """Função principal para execução standalone"""
    try:
        # Inicializar driver global
        if init_driver():
            print("Aplicação iniciada com driver global configurado")
            
            # Criar e executar a aplicação
            app = create_app()
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("Falha ao inicializar driver. Encerrando aplicação.")
    except Exception as e:
        print(f"Erro ao inicializar aplicação: {e}")
        cleanup_global_driver()

# Aplicação standalone (para uso direto)
if __name__ == '__main__':
    main() 