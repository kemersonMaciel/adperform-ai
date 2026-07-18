# 🚀 AdPerform AI — Dashboard de Performance

Dashboard de Performance de Vendas com Diagnóstico Automatizado por IA para
Gestores de Tráfego Pago e Agências de Marketing.

## Stack Técnica
- **Frontend/UI**: Streamlit
- **Processamento**: Python + Pandas
- **Gráficos**: Plotly
- **IA**: Google Gemini 2.0 Flash (via `google-generativeai`)
- **Deploy**: Streamlit Community Cloud (gratuito)

## Estrutura de Arquivos
```
adperform-ai/
├── app.py                    ← Aplicação principal (único arquivo de código)
├── requirements.txt          ← Dependências para o Streamlit Cloud
├── .gitignore                ← Protege o arquivo de secrets
├── README.md                 ← Este arquivo
└── .streamlit/
    └── secrets.toml          ← API Keys locais (NÃO commitar!)
```

## Como Rodar Localmente

### 1. Clone o repositório
```bash
git clone <seu-repo>
cd adperform-ai
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure a API Key localmente
Edite `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIzaSy_sua_chave_aqui"
```

### 5. Execute o app
```bash
streamlit run app.py
```

## Deploy no Streamlit Cloud
Veja o guia completo de configuração de Secrets no arquivo de resposta do projeto.

## Estrutura da Planilha Google Sheets
Para conectar dados reais, crie uma planilha com as colunas abaixo (primeira linha = cabeçalho):

| data       | campanha            | canal      | investimento | impressoes | cliques | conversoes | receita  |
|------------|---------------------|------------|-------------|------------|---------|------------|---------|
| 2024-01-15 | Aquisição - Search  | Google Ads | 850.00       | 102000     | 1530    | 42         | 3150.00 |
| 2024-01-15 | Remarketing - Meta  | Meta Ads   | 420.00       | 58000      | 986     | 61         | 2135.00 |

Depois: **Arquivo → Publicar na Web → CSV → Publicar → copie o link**.
