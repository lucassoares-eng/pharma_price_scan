# Configuração da Integração com Google Gemini AI

## Pré-requisitos

1. **Conta Google Cloud**: Você precisa de uma conta Google Cloud ativa
2. **API Key do Gemini**: Obtenha uma chave de API do Google AI Studio

## Passos para Configuração

### 1. Obter API Key do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Google Gemini API Key
GEMINI_API_KEY=sua_chave_aqui

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ IMPORTANTE**: 
- Nunca commite o arquivo `.env` no Git
- Substitua `sua_chave_aqui` pela chave real obtida no Google AI Studio

### 3. Instalar Dependências

Execute o comando para instalar as novas dependências:

```bash
pip install -r requirements.txt
```

### 4. Testar a Integração

1. Inicie a aplicação:
```bash
python app.py
```

2. Acesse a aplicação no navegador
3. Faça uma busca por um medicamento
4. Selecione uma marca para ver a análise de IA

## Funcionalidades da IA

A integração com Gemini AI fornece:

- **Análise de Posicionamento**: Avalia a competitividade da marca
- **Análise de Preços**: Compara preços com concorrentes
- **Análise de Disponibilidade**: Avalia presença nas farmácias
- **Recomendações**: Sugere insights sobre a marca selecionada

## Estrutura da API

### Endpoint: `/api/pharma/ia/brand-analysis`

**Método**: POST

**Dados de Entrada**:
```json
{
    "brand": "Nome da Marca",
    "position": 1,
    "total_brands": 5,
    "avg_price": 25.50,
    "min_price": 20.00,
    "max_price": 30.00,
    "pharmacy_count": 3,
    "price_diff_text": "-R$ 5.00"
}
```

**Resposta**:
```json
{
    "success": true,
    "analysis": "Texto gerado pela IA...",
    "brand": "Nome da Marca"
}
```

## Tratamento de Erros

- Se a API do Gemini não estiver disponível, o sistema usa análise básica
- Erros de conexão são tratados graciosamente
- Logs de erro são exibidos no console do servidor

## Custos

- Google Gemini oferece créditos gratuitos para novos usuários
- Após o período gratuito, há cobrança por uso
- Consulte [Google AI Studio Pricing](https://ai.google.dev/pricing) para detalhes

## Troubleshooting

### Erro: "GEMINI_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme se a variável `GEMINI_API_KEY` está definida

### Erro: "Invalid API Key"
- Verifique se a chave está correta
- Confirme se a conta tem acesso ao Gemini API

### Erro de Conexão
- Verifique sua conexão com a internet
- Confirme se o Google AI Studio está acessível

## Segurança

- A chave da API nunca é exposta no frontend
- Todas as chamadas são feitas pelo backend
- Use HTTPS em produção
- Considere implementar rate limiting para evitar abuso 