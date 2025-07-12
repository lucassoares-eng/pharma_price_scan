# Guia de Integração - Pharma Price Scanner

Este guia explica como integrar o Pharma Price Scanner em outras aplicações Flask existentes.

## Visão Geral

O Pharma Price Scanner foi projetado para ser facilmente integrado em outras aplicações Flask através de blueprints. Isso permite que você adicione funcionalidade de busca de preços de medicamentos sem modificar significativamente sua aplicação existente.

## Métodos de Integração

### 1. Integração Simples (Recomendado)

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

**Endpoints disponíveis:**
- `POST /api/pharma/search` - Busca medicamentos
- `GET /api/pharma/health` - Status do driver
- `GET /` - Interface web

### 2. Integração com Prefixo Personalizado

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Integrar com prefixo personalizado
integration = integrate_pharma_scanner(app, url_prefix='/medicines')

# Suas rotas existentes
@app.route('/')
def home():
    return "Minha aplicação"

if __name__ == '__main__':
    app.run(debug=True)
```

**Endpoints disponíveis:**
- `POST /medicines/api/pharma/search` - Busca medicamentos
- `GET /medicines/api/pharma/health` - Status do driver
- `GET /medicines/` - Interface web

### 3. Integração Manual

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

if __name__ == '__main__':
    app.run(debug=True)
```

### 4. Usando a Classe de Integração

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

if __name__ == '__main__':
    app.run(debug=True)
```

## Instalação como Pacote

### Instalação Local

```bash
# No diretório do projeto
pip install -e .
```

### Instalação via Git

```bash
pip install git+https://github.com/your-username/pharma_price_scan.git
```

### Uso após Instalação

```python
from flask import Flask
from pharma_price_scanner import integrate_pharma_scanner

app = Flask(__name__)
integration = integrate_pharma_scanner(app)

@app.route('/')
def home():
    return "Minha aplicação"

if __name__ == '__main__':
    app.run(debug=True)
```

## Configuração Avançada

### Configuração do Driver

```python
from flask import Flask
from pharma_integration import PharmaScannerIntegration

app = Flask(__name__)

# Criar integração sem inicializar automaticamente
integration = PharmaScannerIntegration(app, auto_init=False)

# Inicializar manualmente
if integration.init_driver():
    integration.register_blueprints()
else:
    print("Falha ao inicializar driver")

@app.route('/')
def home():
    return "Minha aplicação"
```

### Múltiplas Instâncias

```python
from flask import Flask
from pharma_integration import PharmaScannerIntegration

app = Flask(__name__)

# Criar múltiplas integrações com prefixos diferentes
integration1 = PharmaScannerIntegration(app)
integration1.register_blueprints(url_prefix='/pharma1')

integration2 = PharmaScannerIntegration(app)
integration2.register_blueprints(url_prefix='/pharma2')

@app.route('/')
def home():
    return "Minha aplicação"
```

## Tratamento de Erros

### Verificação de Disponibilidade

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

try:
    integration = integrate_pharma_scanner(app)
    print("Pharma Scanner integrado com sucesso")
except Exception as e:
    print(f"Falha na integração: {e}")
    # Continuar sem o Pharma Scanner

@app.route('/')
def home():
    return "Minha aplicação"
```

### Integração Condicional

```python
from flask import Flask
from pharma_integration import PharmaScannerIntegration

app = Flask(__name__)

# Verificar se as dependências estão disponíveis
try:
    import selenium
    import webdriver_manager
    
    integration = PharmaScannerIntegration(app)
    print("Pharma Scanner disponível")
except ImportError:
    print("Dependências não encontradas - continuando sem Pharma Scanner")

@app.route('/')
def home():
    return "Minha aplicação"
```

## Exemplos de Uso da API

### Busca de Medicamentos

```python
import requests

# Buscar medicamento
response = requests.post('http://localhost:5000/api/pharma/search', 
                        json={'medicine_description': 'paracetamol'})

if response.status_code == 200:
    data = response.json()
    print(f"Resultados encontrados: {data['results']}")
else:
    print(f"Erro: {response.text}")
```

### Verificar Status

```python
import requests

# Verificar status do driver
response = requests.get('http://localhost:5000/api/pharma/health')

if response.status_code == 200:
    data = response.json()
    print(f"Status: {data['status']}")
else:
    print(f"Erro: {response.text}")
```

## Considerações de Performance

### Driver Compartilhado

O sistema utiliza um driver Selenium compartilhado que é:
- Inicializado uma única vez
- Reutilizado por todas as requisições
- Limpo automaticamente ao encerrar a aplicação

### Configuração de Timeout

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Configurar timeout personalizado
app.config['PHARMA_TIMEOUT'] = 60  # segundos

integration = integrate_pharma_scanner(app)
```

## Troubleshooting

### Problemas Comuns

1. **Driver não inicializa**
   - Verifique se o Chrome está instalado
   - Verifique se há permissões para executar o ChromeDriver
   - Verifique a conectividade com a internet

2. **Erro de dependências**
   - Instale as dependências: `pip install -r requirements.txt`
   - Verifique a versão do Python (>= 3.7)

3. **Timeout nas requisições**
   - Aumente o timeout na configuração
   - Verifique a conectividade com os sites das farmácias

### Logs de Debug

```python
import logging

# Configurar logs detalhados
logging.basicConfig(level=logging.DEBUG)

from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)
integration = integrate_pharma_scanner(app)
```

## Suporte

Para suporte técnico ou dúvidas sobre integração:

1. Verifique a documentação no README.md
2. Abra uma issue no GitHub
3. Consulte os exemplos em `integration_example.py`

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes. 