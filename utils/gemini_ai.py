import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

class GeminiAI:
    def __init__(self):
        """Inicializa a integração com Google Gemini AI"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")
        
        # Configurar a API
        genai.configure(api_key=self.api_key)
        
        # Configurar o modelo
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_brand_analysis(self, brand_data):
        """
        Gera análise de marca usando IA
        
        Args:
            brand_data (dict): Dados da marca para análise
            
        Returns:
            str: Texto de análise gerado pela IA
        """
        try:
            # Criar prompt estruturado
            prompt = self._create_analysis_prompt(brand_data)
            
            # Log do prompt para debug
            print("=" * 80)
            print("PROMPT ENVIADO PARA GEMINI IA:")
            print("=" * 80)
            print(prompt)
            print("=" * 80)
            
            # Gerar resposta
            response = self.model.generate_content(prompt)
            
            print("RESPOSTA DA IA:")
            print(response.text.strip())
            print("=" * 80)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Erro ao gerar análise com Gemini: {e}")
            # Fallback para análise básica
            return self._generate_fallback_analysis(brand_data)
    
    def _create_analysis_prompt(self, brand_data):
        """Cria prompt estruturado para análise da marca"""
        
        # Obter farmácias analisadas
        pharmacies_analyzed = brand_data.get('pharmacies_analyzed', [])
        pharmacies_text = ', '.join(pharmacies_analyzed)
        
        # Preparar dados de todos os produtos estruturados como na Lista de Produtos
        products_data = brand_data.get('products_data', [])
        
        # Estruturar produtos como na Lista de Produtos
        products_list = ""
        for product in products_data:
            price_display = f"R$ {product['price']:.2f}" if product['price'] else "N/A"
            original_price_display = f"R$ {product['original_price']:.2f}" if product.get('original_price') else ""
            discount_info = ""
            if product.get('has_discount') and product.get('discount_percentage'):
                discount_info = f" (Original: {original_price_display}, Desconto: {product['discount_percentage']}%)"
            position_info = f" | Posição: {product['position']}" if product.get('position') else ""
            
            products_list += f"- {product['name']} | {product['pharmacy']} | {price_display}{discount_info}{position_info}\n"
        
        prompt = f"""
        Você é um especialista em análise competitiva de mercado farmacêutico brasileiro. Sua missão é analisar o posicionamento da marca {brand_data['brand']} em relação aos seus concorrentes diretos dentro das farmácias analisadas.

        FARMÁCIAS ANALISADAS: {pharmacies_text}
        IMPORTANTE: A análise deve ser feita considerando APENAS essas farmácias.

        FOCO PRINCIPAL: Analise preço e posicionamento da marca {brand_data['brand']} comparando com todas as outras marcas disponíveis.

        LISTA COMPLETA DE PRODUTOS ENCONTRADOS:
        {products_list}

        ANÁLISE REQUERIDA:
        1. COMPETITIVIDADE DE PREÇO: Como {brand_data['brand']} se posiciona em relação aos concorrentes? É mais cara, mais barata ou intermediária?
        2. ESTRATÉGIA DE POSICIONAMENTO: Como está o posicionamento da marca nos sites das farmácias em relação aos concorrentes, está entre os primeiros produtos que aparecem no site?
        3. ESTRATÉGIA DE DESCONTO: Como está a estratégia de desconto da marca em relação aos concorrentes? Oferece descontos mais atrativos?
        4. RECOMENDAÇÕES E INSIGHTS: Recomendações e insights sobre como se posicionar melhor no mercado em relação aos concorrentes.

        Gere uma análise concisa e estratégica (3-4 frases) focando na competitividade de preço e posicionamento, usando linguagem profissional para consumidores brasileiros.
        """
        
        return prompt
    
    def _generate_fallback_analysis(self, brand_data):
        """Gera análise básica quando a IA falha"""
        
        position = brand_data['position']
        total_brands = brand_data['total_brands']
        pharmacy_count = brand_data['pharmacy_count']
        
        if position <= total_brands * 0.3 and pharmacy_count > 1:
            return f"A marca {brand_data['brand']} está entre as opções mais econômicas do mercado, encontrada em {pharmacy_count} farmácias. Isso indica boa competitividade tanto em preço quanto em disponibilidade."
        elif position >= total_brands * 0.7 and pharmacy_count <= 2:
            return f"A marca {brand_data['brand']} apresenta preços acima da média e está disponível em poucas farmácias ({pharmacy_count}), sugerindo menor competitividade frente aos concorrentes."
        else:
            return f"A marca {brand_data['brand']} possui preço intermediário em relação aos concorrentes e está presente em {pharmacy_count} farmácias, oferecendo equilíbrio entre preço e disponibilidade." 