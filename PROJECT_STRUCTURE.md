# Estrutura do Projeto Pharma Price Scan

## Organização de Pastas

```
pharma_price_scan/
├── app.py                          # Aplicação principal Flask
├── requirements.txt                 # Dependências Python
├── setup.py                        # Configuração do projeto
├── README.md                       # Documentação principal
├── INTEGRATION.md                  # Guia de integração
├── integration_example.py          # Exemplo de integração
├── pharma_integration.py           # Módulo de integração
│
├── utils/                          # Utilitários do projeto
│   ├── __init__.py
│   └── product_unifier.py         # Unificador de produtos similares
│
├── tests/                          # Testes do projeto
│   ├── __init__.py
│   ├── test_unifier.py            # Teste do unificador
│   ├── test_raia_scraper.py       # Teste do scraper Raia
│   └── test_sao_joao_scraper.py   # Teste do scraper São João
│
├── scrapers/                       # Scrapers das farmácias
│   ├── __init__.py
│   ├── base_scraper.py            # Classe base para scrapers
│   ├── droga_raia.py              # Scraper da Droga Raia
│   ├── sao_joao.py                # Scraper da São João
│   └── example_scraper.py         # Exemplo de scraper
│
├── static/                         # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/
│   │   └── style.css              # Estilos da aplicação
│   ├── js/
│   │   └── app.js                 # JavaScript da aplicação
│   └── logos/                     # Logos das farmácias
│
├── templates/                      # Templates HTML
│   └── index.html                 # Página principal
│
├── chromedriver_bin/              # Binários do ChromeDriver
│   └── chromedriver-win64/
│
└── venv/                          # Ambiente virtual Python
```

## Funcionalidades Principais

### 1. Unificação de Produtos (`utils/product_unifier.py`)
- **Propósito**: Unifica produtos similares de diferentes farmácias
- **Funcionalidades**:
  - Análise de similaridade de texto
  - Normalização de nomes e descrições
  - Agrupamento de produtos similares
  - Identificação do melhor preço entre variações

### 2. API de Busca (`app.py`)
- **Endpoints**:
  - `/api/pharma/search`: Busca produtos em todas as farmácias
  - `/api/pharma/search_unified`: Busca e retorna apenas produtos unificados
  - `/api/pharma/health`: Verificação de saúde da API

### 3. Interface Web
- **Página principal**: `/`
- **Funcionalidades**:
  - Busca de medicamentos
  - Visualização de produtos unificados
  - Gráficos de preços
  - Estatísticas comparativas

## Como Usar

### 1. Instalação
```bash
pip install -r requirements.txt
```

### 2. Execução
```bash
python app.py
```

### 3. Testes
```bash
# Teste do unificador
python tests/test_unifier.py

# Teste dos scrapers
python tests/test_raia_scraper.py
python tests/test_sao_joao_scraper.py
```

## Exemplo de Uso da API

### Busca com produtos unificados:
```python
import requests

response = requests.post('http://localhost:5000/api/pharma/search', 
    json={'medicine_description': 'ibuprofeno 600mg 20 comprimidos'})

data = response.json()
unified_products = data['unified_results']['unified_products']

for product in unified_products:
    print(f"{product['unified_name']} - R$ {product['best_price']:.2f}")
```

## Resultados do Teste

O teste do unificador demonstrou:
- **6 produtos originais** → **3 produtos unificados**
- Identificação correta de produtos similares
- Agrupamento de variações do mesmo medicamento
- Identificação do melhor preço entre variações

## Próximos Passos

1. **Melhorar algoritmos de similaridade**
2. **Adicionar mais farmácias**
3. **Implementar cache de resultados**
4. **Adicionar mais testes**
5. **Melhorar interface web** 