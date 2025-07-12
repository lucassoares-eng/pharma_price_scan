"""
Módulo de integração para o Pharma Price Scanner.
Facilita a inclusão do sistema em outras aplicações Flask.
"""

from flask import Blueprint
from app import get_blueprints, init_driver, cleanup_global_driver
import atexit

class PharmaScannerIntegration:
    """Classe para facilitar a integração do Pharma Scanner"""
    
    def __init__(self, app=None, auto_init=True):
        """
        Inicializa a integração do Pharma Scanner
        
        Args:
            app: Aplicação Flask (opcional)
            auto_init: Se deve inicializar automaticamente o driver
        """
        self.app = app
        self.driver_initialized = False
        
        if app is not None:
            self.init_app(app)
        
        if auto_init:
            self.init_driver()
    
    def init_app(self, app):
        """Inicializa a integração com uma aplicação Flask"""
        self.app = app
        
        # Registrar função de limpeza
        atexit.register(self.cleanup)
    
    def init_driver(self):
        """Inicializa o driver global"""
        try:
            if init_driver():
                self.driver_initialized = True
                print("Driver do Pharma Scanner inicializado com sucesso")
                return True
            else:
                print("Falha ao inicializar driver do Pharma Scanner")
                return False
        except Exception as e:
            print(f"Erro ao inicializar driver: {e}")
            return False
    
    def register_blueprints(self, app=None, url_prefix=None):
        """
        Registra os blueprints do Pharma Scanner
        
        Args:
            app: Aplicação Flask (usa self.app se não fornecido)
            url_prefix: Prefixo personalizado para as rotas
        """
        if app is None:
            app = self.app
        
        if app is None:
            raise ValueError("Aplicação Flask não fornecida")
        
        # Obter blueprints
        pharma_blueprints = get_blueprints()
        
        # Registrar com prefixo personalizado se fornecido
        if url_prefix:
            for blueprint in pharma_blueprints:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
        else:
            for blueprint in pharma_blueprints:
                app.register_blueprint(blueprint)
        
        print(f"Blueprints do Pharma Scanner registrados em {app.name}")
        return True
    
    def get_blueprints(self):
        """Retorna os blueprints do Pharma Scanner"""
        return get_blueprints()
    
    def cleanup(self):
        """Limpa recursos do driver"""
        if self.driver_initialized:
            cleanup_global_driver()
            self.driver_initialized = False
            print("Recursos do Pharma Scanner limpos")

def integrate_pharma_scanner(app, auto_init=True, url_prefix=None):
    """
    Função de conveniência para integrar o Pharma Scanner
    
    Args:
        app: Aplicação Flask
        auto_init: Se deve inicializar automaticamente o driver
        url_prefix: Prefixo personalizado para as rotas
    
    Returns:
        PharmaScannerIntegration: Instância da integração
    """
    integration = PharmaScannerIntegration(app, auto_init=auto_init)
    
    if auto_init and integration.driver_initialized:
        integration.register_blueprints(url_prefix=url_prefix)
    
    return integration

def create_pharma_app(config=None):
    """
    Cria uma aplicação Flask com o Pharma Scanner integrado
    
    Args:
        config: Configurações da aplicação
    
    Returns:
        Flask app: Aplicação Flask com Pharma Scanner
    """
    from app import create_app
    return create_app(config)

# Exemplo de uso como decorator
def pharma_scanner_blueprint(url_prefix=None):
    """
    Decorator para criar um blueprint do Pharma Scanner
    
    Args:
        url_prefix: Prefixo para as rotas
    
    Returns:
        Blueprint: Blueprint do Pharma Scanner
    """
    def decorator(app):
        integration = integrate_pharma_scanner(app, auto_init=True, url_prefix=url_prefix)
        return integration
    return decorator 