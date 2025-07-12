# Pharma Price Scanner

Sistema de busca de preços de medicamentos em diferentes farmácias usando web scraping com Selenium.

## Características

- **Driver Selenium Compartilhado**: O driver é inicializado uma única vez na aplicação e reutilizado por todos os scrapers
- **Gerenciamento Automático do ChromeDriver**: Verifica e atualiza automaticamente o ChromeDriver conforme necessário
- **Múltiplas Farmácias**: Suporte para múltiplas farmácias com scrapers independentes
- **Interface Web**: Interface simples para busca de medicamentos
- **API REST**: Endpoint para busca programática

## Estrutura do Projeto

```
pharma_price_scan/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py   # Classe base para todos os scrapers
│   ├── droga_raia.py     # Scraper para Droga Raia
│   └── example_scraper.py # Exemplo de novo scraper
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

### Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### Endpoints Disponíveis

- `GET /`: Interface web para busca de medicamentos
- `POST /api/search`: API para busca de medicamentos
- `GET /api/health`: Verificar status do driver

### Exemplo de Uso da API

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"medicine_description": "paracetamol"}'
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