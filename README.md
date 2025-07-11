# Comparador de Preços de Medicamentos

Um aplicativo Flask Python que permite buscar e comparar preços de medicamentos em diferentes farmácias online.

## Funcionalidades

- Interface web moderna e responsiva
- Busca de medicamentos por descrição
- Webscraping automático de farmácias
- Exibição de preços, descontos e informações dos produtos
- Suporte a múltiplas farmácias (atualmente Droga Raia)

## Estrutura do Projeto

```
pharma_price_scan/
├── app.py                 # Aplicativo Flask principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── scrapers/             # Módulo de scrapers
│   ├── __init__.py
│   └── droga_raia.py    # Scraper para Droga Raia
└── templates/            # Templates HTML
    └── index.html        # Interface principal
```

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd pharma_price_scan
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o aplicativo:
```bash
python app.py
```

2. Abra o navegador e acesse:
```
http://localhost:5000
```

3. Digite a descrição do medicamento (ex: "ibuprofeno 600mg comprimido") e clique em "Buscar"

## Como Funciona

### Backend (Flask)
- **app.py**: Aplicativo principal com rotas para interface web e API
- **API endpoint**: `/api/search` - Recebe descrição do medicamento e retorna resultados de todas as farmácias

### Scrapers
- **droga_raia.py**: Scraper específico para o site Droga Raia
- Estrutura modular permite adicionar facilmente novos scrapers para outras farmácias

### Interface Web
- Interface moderna com Bootstrap 5
- Busca assíncrona via JavaScript
- Exibição organizada dos resultados por farmácia
- Suporte a imagens, preços, descontos e links dos produtos

## Adicionando Novas Farmácias

Para adicionar uma nova farmácia:

1. Crie um novo arquivo em `scrapers/` (ex: `scrapers/farmacia_nova.py`)
2. Implemente uma classe que herde de um padrão comum ou seja compatível
3. Adicione o scraper ao dicionário em `app.py`

Exemplo de estrutura para novo scraper:
```python
class NovaFarmaciaScraper:
    def __init__(self):
        self.base_url = "https://www.novafarmacia.com.br"
    
    def search(self, medicine_description):
        # Implementar lógica de busca
        return {
            'pharmacy': 'Nova Farmácia',
            'products': [...],
            'total_products': len(products)
        }
```

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Webscraping**: BeautifulSoup4, Requests
- **Interface**: Design responsivo com gradientes e animações

## Limitações

- O webscraping pode ser afetado por mudanças na estrutura dos sites
- Alguns sites podem bloquear requisições automatizadas
- A velocidade de busca depende da resposta dos sites das farmácias

## Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste o funcionamento
5. Envie um Pull Request

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.