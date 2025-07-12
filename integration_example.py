"""
Exemplo de como integrar o Pharma Price Scanner em outro aplicativo Flask existente.
"""

from flask import Flask, render_template
from app import get_blueprints, init_driver, cleanup_global_driver
import atexit

# Aplicação Flask existente
app = Flask(__name__)

# Configurações da aplicação existente
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DEBUG'] = True

# Rotas da aplicação existente
@app.route('/')
def home():
    """Página inicial da aplicação existente"""
    return render_template('home.html')

@app.route('/about')
def about():
    """Página sobre da aplicação existente"""
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard da aplicação existente"""
    return render_template('dashboard.html')

# Integrar os blueprints do Pharma Scanner
def integrate_pharma_scanner():
    """Integra o Pharma Scanner na aplicação existente"""
    try:
        # Inicializar o driver global
        if init_driver():
            print("Driver do Pharma Scanner inicializado com sucesso")
            
            # Obter e registrar os blueprints
            pharma_blueprints = get_blueprints()
            for blueprint in pharma_blueprints:
                app.register_blueprint(blueprint)
                print(f"Blueprint {blueprint.name} registrado")
            
            # Configurar limpeza do driver
            atexit.register(cleanup_global_driver)
            
            return True
        else:
            print("Falha ao inicializar driver do Pharma Scanner")
            return False
            
    except Exception as e:
        print(f"Erro ao integrar Pharma Scanner: {e}")
        return False

# Exemplo de uso com prefixo personalizado
def integrate_with_custom_prefix():
    """Integra o Pharma Scanner com prefixos personalizados"""
    try:
        # Inicializar o driver global
        if init_driver():
            print("Driver do Pharma Scanner inicializado com sucesso")
            
            # Obter os blueprints
            pharma_api, pharma_web = get_blueprints()
            
            # Registrar com prefixos personalizados
            app.register_blueprint(pharma_api, url_prefix='/medicines/api')
            app.register_blueprint(pharma_web, url_prefix='/medicines')
            
            print("Pharma Scanner integrado com prefixos personalizados")
            
            # Configurar limpeza do driver
            atexit.register(cleanup_global_driver)
            
            return True
        else:
            print("Falha ao inicializar driver do Pharma Scanner")
            return False
            
    except Exception as e:
        print(f"Erro ao integrar Pharma Scanner: {e}")
        return False

# Exemplo de integração condicional
def integrate_conditionally():
    """Integra o Pharma Scanner apenas se as dependências estiverem disponíveis"""
    try:
        # Verificar se as dependências estão disponíveis
        import selenium
        import webdriver_manager
        
        # Tentar inicializar o driver
        if init_driver():
            print("Pharma Scanner disponível - integrando...")
            
            # Registrar blueprints
            pharma_blueprints = get_blueprints()
            for blueprint in pharma_blueprints:
                app.register_blueprint(blueprint)
            
            # Configurar limpeza
            atexit.register(cleanup_global_driver)
            
            return True
        else:
            print("Pharma Scanner não disponível - continuando sem ele")
            return False
            
    except ImportError:
        print("Dependências do Pharma Scanner não encontradas - continuando sem ele")
        return False
    except Exception as e:
        print(f"Erro ao verificar Pharma Scanner: {e}")
        return False

if __name__ == '__main__':
    # Exemplo 1: Integração simples
    if integrate_pharma_scanner():
        print("Pharma Scanner integrado com sucesso!")
        print("Endpoints disponíveis:")
        print("  - /api/pharma/search (POST)")
        print("  - /api/pharma/health (GET)")
        print("  - / (interface web)")
    else:
        print("Falha na integração do Pharma Scanner")
    
    # Exemplo 2: Integração com prefixos personalizados
    # if integrate_with_custom_prefix():
    #     print("Pharma Scanner integrado com prefixos personalizados!")
    #     print("Endpoints disponíveis:")
    #     print("  - /medicines/api/search (POST)")
    #     print("  - /medicines/api/health (GET)")
    #     print("  - /medicines/ (interface web)")
    
    # Exemplo 3: Integração condicional
    # if integrate_conditionally():
    #     print("Pharma Scanner integrado condicionalmente!")
    # else:
    #     print("Aplicação executando sem Pharma Scanner")
    
    # Executar a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000) 