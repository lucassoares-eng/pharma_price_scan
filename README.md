# Pharma Price Scanner

Sistema de busca de preços de medicamentos em diferentes farmácias usando web scraping com Selenium.

## Características

- **Driver Selenium Compartilhado**: O driver é inicializado uma única vez na aplicação e reutilizado por todos os scrapers
- **Gerenciamento Automático do ChromeDriver**: Verifica e atualiza automaticamente o ChromeDriver conforme necessário
- **Múltiplas Farmácias**: Suporte para múltiplas farmácias com scrapers independentes
- **Interface Web**: Interface simples para busca de medicamentos
- **API REST**: Endpoint para busca programática
- **Arquitetura Modular**: Blueprints Flask para fácil integração em outras aplicações
- **Arquivos Estáticos Organizados**: CSS e JavaScript separados em arquivos independentes

## Estrutura do Projeto

```
pharma_price_scan/
├── app.py                 # Aplicação Flask principal com blueprints
├── requirements.txt       # Dependências Python
├── integration_example.py # Exemplo de integração em outras apps
├── pharma_integration.py # Módulo de integração facilitada
├── setup.py              # Configuração para instalação como pacote
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py   # Classe base para todos os scrapers
│   ├── droga_raia.py     # Scraper para Droga Raia
│   ├── sao_joao.py       # Scraper para São João
│   └── example_scraper.py # Exemplo de novo scraper
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS da aplicação
│   └── js/
│       └── app.js        # JavaScript da aplicação
└── templates/
    └── index.html         # Interface web
```

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd pharma_price_scan
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Executar a Aplicação Standalone

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### Endpoints Disponíveis

- `GET /`: Interface web para busca de medicamentos
- `POST /api/pharma/search`: API para busca de medicamentos
- `GET /api/pharma/health`: Verificar status do driver

### Exemplo de Uso da API

```bash
curl -X POST http://localhost:5000/api/pharma/search \
  -H "Content-Type: application/json" \
  -d '{"medicine_description": "ibuprofeno 600mg 20"}'
```

### Farmácias Suportadas

- **Droga Raia**: https://www.drogaraia.com.br
- **São João**: https://www.saojoaofarmacias.com.br

## Integração em Outras Aplicações Flask

### Método 1: Integração Simples

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Integrar o Pharma Scanner
integration = integrate_pharma_scanner(app)

# Suas rotas existentes
@app.route('/')
def home():
    return "Minha aplicação"

if __name__ == '__main__':
    app.run(debug=True)
```

### Método 2: Integração com Prefixo Personalizado

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Integrar com prefixo personalizado
integration = integrate_pharma_scanner(app, url_prefix='/medicines')

# Agora os endpoints estarão em:
# - /medicines/api/pharma/search
# - /medicines/api/pharma/health
# - /medicines/ (interface web)
```

### Método 3: Integração Manual

```python
from flask import Flask
from app import get_blueprints, init_driver, cleanup_global_driver
import atexit

app = Flask(__name__)

# Inicializar driver
if init_driver():
    # Registrar blueprints
    pharma_blueprints = get_blueprints()
    for blueprint in pharma_blueprints:
        app.register_blueprint(blueprint)
    
    # Configurar limpeza
    atexit.register(cleanup_global_driver)

# Suas rotas
@app.route('/')
def home():
    return "Minha aplicação"
```

### Método 4: Usando a Classe de Integração

```python
from flask import Flask
from pharma_integration import PharmaScannerIntegration

app = Flask(__name__)

# Criar integração
integration = PharmaScannerIntegration(app)

# Registrar blueprints quando necessário
integration.register_blueprints(url_prefix='/pharma')

# Suas rotas
@app.route('/')
def home():
    return "Minha aplicação"
```

## Adicionando Novos Scrapers

Para adicionar um novo scraper para uma nova farmácia:

1. Crie um novo arquivo em `scrapers/` (ex: `scrapers/nova_farmacia.py`)

2. Implemente a classe do scraper seguindo o padrão:

```python
from .base_scraper import BaseScraper

class NovaFarmaciaScraper(BaseScraper):
    def __init__(self, driver=None):
        super().__init__(
            base_url="https://www.nova-farmacia.com",
            search_url="https://www.nova-farmacia.com/search",
            pharmacy_name="Nova Farmácia",
            driver=driver  # Importante: aceitar o driver compartilhado
        )
    
    def search(self, medicine_description):
        # Implementar lógica de busca
        pass
    
    def _extract_products(self, soup):
        # Implementar extração de produtos
        pass
    
    def _extract_product_info(self, product_element):
        # Implementar extração de informações do produto
        pass
```

3. Adicione o novo scraper ao `app.py`:

```python
from scrapers.nova_farmacia import NovaFarmaciaScraper

# Na função search_medicines:
scrapers = {
    'droga_raia': DrogaRaiaScraper(driver=driver),
    'nova_farmacia': NovaFarmaciaScraper(driver=driver)  # Adicionar aqui
}
```

## Sistema de Driver Compartilhado

O sistema utiliza um driver Selenium global que é:

1. **Inicializado uma única vez** quando a aplicação inicia
2. **Reutilizado** por todos os scrapers
3. **Gerenciado automaticamente** com verificação e atualização do ChromeDriver
4. **Limpo adequadamente** quando a aplicação é encerrada

### Vantagens

- **Performance**: Evita overhead de inicializar múltiplos drivers
- **Recursos**: Menor uso de memória e CPU
- **Confiabilidade**: Menos instâncias do Chrome para gerenciar
- **Manutenção**: Centralização do gerenciamento do driver

### Gerenciamento do ChromeDriver

O sistema automaticamente:

1. Detecta a versão do Chrome instalada
2. Baixa o ChromeDriver compatível se necessário
3. Usa fallback para ChromeDriverManager se houver problemas
4. Configura o driver com opções otimizadas para web scraping

## Blueprints Disponíveis

O sistema expõe dois blueprints principais:

### `pharma_api` (API REST)
- `POST /search`: Busca medicamentos
- `GET /health`: Verificar status do driver

### `pharma_web` (Interface Web)
- `GET /`: Interface web para busca

## Arquivos Estáticos

### CSS (`static/css/style.css`)
- Estilos responsivos e modernos
- Gradientes e animações
- Componentes personalizados para cards, gráficos e estatísticas

### JavaScript (`static/js/app.js`)
- Lógica de busca e exibição de resultados
- Criação e interação com gráficos Chart.js
- Análise comparativa de preços
- Gerenciamento de estado da aplicação

## Logs e Debugging

O sistema inclui logs detalhados para debugging:

- Inicialização do driver
- Status das requisições
- Extração de produtos
- Erros e exceções

Para ver logs mais detalhados, ajuste o nível de logging no código.

## Dependências

- Flask: Framework web
- Selenium: Automação de navegador
- BeautifulSoup4: Parsing HTML
- webdriver-manager: Gerenciamento automático do ChromeDriver
- requests: Requisições HTTP

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente o novo scraper seguindo o padrão estabelecido
4. Teste adequadamente
5. Envie um pull request

## Licença

Este projeto está sob a licença MIT.