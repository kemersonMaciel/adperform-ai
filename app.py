# ============================================================
# 🚀 AdPerform AI — Dashboard de Performance com Diagnóstico por IA
#
# Nicho   : Gestores de Tráfego Pago e Agências de Marketing
# Stack   : Streamlit + Pandas + Plotly + Gemini AI
# Deploy  : Streamlit Community Cloud (gratuito)
# Execução: streamlit run app.py
# ============================================================

from __future__ import annotations

import io
import random
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── google-generativeai é importado dentro da função para evitar
#    erro de inicialização quando a lib ainda não está configurada ──

# =============================================================
# ⚙️  CONFIGURAÇÃO DA PÁGINA
#     Deve ser o PRIMEIRO comando Streamlit do script
# =============================================================
st.set_page_config(
    page_title="AdPerform AI | Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System completo: Navy Dark + Blue Accent ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --navy:         #080E1C;
    --navy-card:    #0F172A;
    --navy-hover:   #162035;
    --navy-border:  rgba(59,130,246,0.13);
    --blue:         #2563EB;
    --blue-light:   #3B82F6;
    --blue-glow:    rgba(37,99,235,0.18);
    --green:        #10B981;
    --green-dim:    rgba(16,185,129,0.12);
    --red:          #EF4444;
    --red-dim:      rgba(239,68,68,0.12);
    --yellow:       #F59E0B;
    --text-1:       #F1F5F9;
    --text-2:       #94A3B8;
    --text-3:       #64748B;
}

/* ── Base ── */
html, body, .stApp {
    background-color: var(--navy) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-1) !important;
}
.block-container { padding-top: 1.4rem !important; padding-bottom: 2rem !important; }
#MainMenu, footer { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy-card) !important;
    border-right: 1px solid var(--navy-border) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.2rem !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stRadio label { color: var(--text-2) !important; font-size: 0.83rem !important; }
[data-testid="stSidebar"] h2 { color: var(--text-1) !important; font-size: 1.1rem !important; font-weight: 700 !important; }

/* ── Inputs ── */
.stTextInput input, .stFileUploader > div {
    background: #0A111F !important;
    border: 1px solid var(--navy-border) !important;
    border-radius: 8px !important;
    color: var(--text-1) !important;
    font-size: 0.83rem !important;
}
.stTextInput input:focus { border-color: var(--blue-light) !important; box-shadow: 0 0 0 3px var(--blue-glow) !important; }

/* ── Botão primário ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; letter-spacing: 0.02em !important;
    color: #fff !important; transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
    box-shadow: 0 4px 20px rgba(37,99,235,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--navy-card);
    border: 1px solid var(--navy-border);
    border-radius: 14px;
    padding: 18px 20px 16px;
    position: relative; overflow: hidden;
    transition: all 0.25s ease;
    height: 110px;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--blue), var(--blue-light), transparent);
}
.kpi-card:hover { border-color: rgba(59,130,246,0.32); background: var(--navy-hover); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.kpi-label { font-size: 0.68rem; font-weight: 700; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 8px; }
.kpi-value { font-size: 1.65rem; font-weight: 800; color: var(--text-1); line-height: 1; margin-bottom: 6px; letter-spacing: -0.02em; }
.kpi-delta-pos { font-size: 0.72rem; color: var(--green); font-weight: 600; display: flex; align-items: center; gap: 3px; }
.kpi-delta-neg { font-size: 0.72rem; color: var(--red); font-weight: 600; }
.kpi-delta-neu { font-size: 0.72rem; color: var(--text-3); font-weight: 500; }

/* ── Finance Cards ── */
.fin-card {
    background: var(--navy-card);
    border: 1px solid var(--navy-border);
    border-radius: 12px;
    padding: 16px 20px;
}
.fin-label { font-size: 0.68rem; font-weight: 700; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.fin-value { font-size: 1.3rem; font-weight: 700; color: var(--text-1); }
.fin-value.green { color: var(--green); }
.fin-value.red   { color: var(--red); }
.fin-sub { font-size: 0.7rem; color: var(--text-3); margin-top: 3px; }

/* ── Header Banner ── */
.dash-header {
    background: linear-gradient(135deg, #0D1F3C 0%, #080E1C 55%, #0A1529 100%);
    border: 1px solid var(--navy-border);
    border-radius: 16px;
    padding: 26px 30px;
    margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.dash-header::after {
    content: '';
    position: absolute; top: -80px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(37,99,235,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.dash-title { font-size: 1.85rem; font-weight: 800; color: var(--text-1); margin: 0 0 5px 0; letter-spacing: -0.03em; }
.dash-sub   { font-size: 0.85rem; color: var(--text-2); margin: 0; }
.dash-badges { display: flex; gap: 7px; margin-top: 14px; flex-wrap: wrap; }
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 20px;
    font-size: 0.67rem; font-weight: 700; letter-spacing: 0.05em;
}
.badge-blue   { background: rgba(37,99,235,0.14); color: #93C5FD; border: 1px solid rgba(37,99,235,0.28); }
.badge-green  { background: rgba(16,185,129,0.12); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.28); }
.badge-yellow { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.25); }

/* ── Section Title ── */
.sec-title {
    font-size: 0.65rem; font-weight: 800; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.12em;
    margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;
}
.sec-title::after { content: ''; flex: 1; height: 1px; background: var(--navy-border); }

/* ── Source Badge ── */
.source-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(37,99,235,0.07); border: 1px solid rgba(37,99,235,0.18);
    border-radius: 6px; padding: 5px 12px;
    font-size: 0.72rem; color: #93C5FD; margin-bottom: 18px;
    font-weight: 500;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--navy-border) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text-2) !important; font-size: 0.82rem !important; font-weight: 600 !important; }

/* ── Divider ── */
hr { border-color: var(--navy-border) !important; }

/* ── Alert / Info ── */
[data-testid="stAlert"] { background: rgba(37,99,235,0.07) !important; border-color: rgba(37,99,235,0.2) !important; border-radius: 10px !important; }

/* ── Chat message (AI) ── */
[data-testid="stChatMessage"] {
    background: var(--navy-card) !important;
    border: 1px solid var(--navy-border) !important;
    border-radius: 14px !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid var(--navy-border) !important;
    color: var(--text-2) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: var(--blue-light) !important;
    color: var(--text-1) !important;
    background: var(--blue-glow) !important;
}

/* ── Success / Warning ── */
[data-testid="stNotification"] { border-radius: 10px !important; }

/* ── Sidebar logo area ── */
.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 4px 0 16px 0;
    border-bottom: 1px solid var(--navy-border);
    margin-bottom: 16px;
}
.sidebar-logo-icon { font-size: 1.6rem; }
.sidebar-logo-text { line-height: 1.2; }
.sidebar-logo-title { font-size: 1rem; font-weight: 800; color: var(--text-1); }
.sidebar-logo-sub   { font-size: 0.67rem; color: var(--text-3); font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; }

/* ── Section headers ── */
.sidebar-section {
    font-size: 0.65rem; font-weight: 800; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.1em; margin: 16px 0 8px 0;
}
</style>
""", unsafe_allow_html=True)


# =============================================================
# 📊 MÓDULO 1 — DADOS
#     Dados simulados (demo) e carregamento via Google Sheets
# =============================================================

def gerar_dados_simulados() -> pd.DataFrame:
    """
    Cria um DataFrame com 60 dias de dados realistas de campanhas de tráfego pago.
    Usado como fallback quando nenhuma planilha está conectada.

    Colunas geradas:
        data | campanha | canal | investimento | impressoes
        cliques | conversoes | receita
    """
    random.seed(42)

    campanhas_config = [
        {
            "nome":      "Aquisição - Google Search",
            "canal":     "Google Ads",
            "budget":    900.0,
            "cpc_min":   1.80,    # CPC mínimo realista (R$)
            "cpc_max":   3.50,    # CPC máximo realista (R$)
            "ctr_min":   0.020,   # CTR mínimo (2%)
            "ctr_max":   0.045,   # CTR máximo (4.5%)
            "taxa_conv": 0.032,   # taxa de conversão base
            "ticket":    380.0,   # ticket médio base
        },
        {
            "nome":      "Remarketing - Meta Ads",
            "canal":     "Meta Ads",
            "budget":    450.0,
            "cpc_min":   0.90,
            "cpc_max":   2.20,
            "ctr_min":   0.015,
            "ctr_max":   0.040,
            "taxa_conv": 0.055,
            "ticket":    315.0,
        },
        {
            "nome":      "Prospecting - Meta Ads",
            "canal":     "Meta Ads",
            "budget":    650.0,
            "cpc_min":   0.70,
            "cpc_max":   1.80,
            "ctr_min":   0.008,
            "ctr_max":   0.025,
            "taxa_conv": 0.017,
            "ticket":    305.0,
        },
        {
            "nome":      "Branded - Google Search",
            "canal":     "Google Ads",
            "budget":    200.0,
            "cpc_min":   0.50,
            "cpc_max":   1.20,
            "ctr_min":   0.060,
            "ctr_max":   0.120,
            "taxa_conv": 0.080,
            "ticket":    405.0,
        },
    ]

    registros = []
    hoje = datetime.now()

    for i in range(60):
        data = hoje - timedelta(days=59 - i)
        eh_fds = data.weekday() >= 5  # sábado ou domingo

        for camp in campanhas_config:
            # Fim de semana penaliza campanhas de aquisição (comportamento B2B)
            fator_dia    = 0.62 if eh_fds and "Aquisição" in camp["nome"] else 1.0
            fator_random = random.uniform(0.78, 1.28)
            fator_total  = fator_dia * fator_random

            investimento = round(camp["budget"] * fator_total, 2)

            # CPC realista → determina cliques (evita CPC irreal de R$0,12)
            cpc_dia  = random.uniform(camp["cpc_min"], camp["cpc_max"])
            cliques  = max(1, int(investimento / cpc_dia))

            # Impressões calculadas pelo CTR (não pelo investimento direto)
            ctr_dia    = random.uniform(camp["ctr_min"], camp["ctr_max"])
            impressoes = max(cliques, int(cliques / ctr_dia))
            conversoes   = max(0, int(
                cliques * random.uniform(camp["taxa_conv"] * 0.4, camp["taxa_conv"] * 1.9)
            ))
            receita = round(
                conversoes * random.uniform(camp["ticket"] * 0.80, camp["ticket"] * 1.35), 2
            )

            registros.append({
                "data":         data.strftime("%Y-%m-%d"),
                "campanha":     camp["nome"],
                "canal":        camp["canal"],
                "investimento": investimento,
                "impressoes":   impressoes,
                "cliques":      cliques,
                "conversoes":   conversoes,
                "receita":      receita,
            })

    return pd.DataFrame(registros)


@st.cache_data(ttl=300)  # Re-carrega a planilha a cada 5 min
def carregar_dados_planilha(url_csv: str) -> Optional[pd.DataFrame]:
    """
    Carrega dados de uma planilha Google Sheets via URL CSV público.

    Como publicar a planilha:
        1. Abra a planilha → Arquivo → Publicar na Web
        2. Selecione a aba desejada → Formato: CSV → clique em Publicar
        3. Copie o link gerado e cole na sidebar do app

    Colunas obrigatórias (exatamente esses nomes, em minúsculo):
        data | campanha | canal | investimento | impressoes
        cliques | conversoes | receita

    Returns:
        DataFrame limpo ou None em caso de erro
    """
    try:
        df = pd.read_csv(url_csv)

        # Normaliza nomes de coluna: remove espaços e converte para minúsculo
        df.columns = df.columns.str.strip().str.lower()

        colunas_esperadas = [
            "data", "campanha", "canal", "investimento",
            "impressoes", "cliques", "conversoes", "receita",
        ]
        faltando = [c for c in colunas_esperadas if c not in df.columns]
        if faltando:
            st.error(f"❌ Colunas ausentes na planilha: {faltando}")
            return None

        # Conversão e limpeza de tipos
        df["data"]         = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
        df["investimento"] = pd.to_numeric(df["investimento"], errors="coerce")
        df["receita"]      = pd.to_numeric(df["receita"],      errors="coerce")
        df["impressoes"]   = pd.to_numeric(df["impressoes"],   errors="coerce")
        df["cliques"]      = pd.to_numeric(df["cliques"],      errors="coerce")
        df["conversoes"]   = pd.to_numeric(df["conversoes"],   errors="coerce")

        return df.dropna(subset=["data", "investimento"])

    except Exception as exc:
        st.error(f"❌ Falha ao carregar planilha: {exc}")
        return None


def gerar_template_excel() -> bytes:
    """
    Gera um arquivo Excel (.xlsx) de template com a estrutura correta
    de colunas e 4 linhas de exemplo.

    O cliente baixa, preenche com dados reais exportados do Google Ads
    ou Meta Ads, e sobe no app via file uploader.
    """
    df_template = pd.DataFrame({
        "data":         ["2024-01-15", "2024-01-15", "2024-01-16", "2024-01-16"],
        "campanha":     ["Aquisição - Google Search", "Remarketing - Meta Ads",
                         "Aquisição - Google Search", "Remarketing - Meta Ads"],
        "canal":        ["Google Ads", "Meta Ads", "Google Ads", "Meta Ads"],
        "investimento": [850.00, 420.00, 910.00, 395.00],
        "impressoes":   [42500, 28000, 45200, 26800],
        "cliques":      [1275, 840, 1356, 804],
        "conversoes":   [38, 46, 41, 50],
        "receita":      [3150.00, 2135.00, 3380.00, 2280.00],
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_template.to_excel(writer, index=False, sheet_name="Dados")

        instrucoes = pd.DataFrame({
            "Coluna":      ["data", "campanha", "canal", "investimento",
                            "impressoes", "cliques", "conversoes", "receita"],
            "Tipo":        ["Data (AAAA-MM-DD)", "Texto", "Texto", "Número decimal",
                            "Número inteiro", "Número inteiro", "Número inteiro", "Número decimal"],
            "Exemplo":     ["2024-01-15", "Aquisição - Google Search", "Google Ads",
                            "850.00", "42500", "1275", "38", "3150.00"],
            "Obrigatório": ["Sim"] * 8,
        })
        instrucoes.to_excel(writer, index=False, sheet_name="Instruções")

    buffer.seek(0)
    return buffer.getvalue()


def carregar_dados_upload(arquivo) -> Optional[pd.DataFrame]:
    """
    Carrega dados de um arquivo CSV ou Excel enviado via st.file_uploader.

    Formatos suportados: .csv | .xlsx | .xls

    Returns:
        DataFrame limpo ou None em caso de erro
    """
    try:
        nome = arquivo.name.lower()

        if nome.endswith(".csv"):
            df = pd.read_csv(arquivo)
        elif nome.endswith((".xlsx", ".xls")):
            df = pd.read_excel(arquivo, engine="openpyxl")
        else:
            st.error("❌ Formato não suportado. Use CSV ou Excel (.xlsx / .xls)")
            return None

        df.columns = df.columns.str.strip().str.lower()

        colunas_esperadas = [
            "data", "campanha", "canal", "investimento",
            "impressoes", "cliques", "conversoes", "receita",
        ]
        faltando = [c for c in colunas_esperadas if c not in df.columns]
        if faltando:
            st.error(
                f"❌ Colunas ausentes no arquivo: **{faltando}**  \n"
                "Baixe o template na sidebar para ver o formato correto."
            )
            return None

        df["data"]         = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
        df["investimento"] = pd.to_numeric(df["investimento"], errors="coerce")
        df["receita"]      = pd.to_numeric(df["receita"],      errors="coerce")
        df["impressoes"]   = pd.to_numeric(df["impressoes"],   errors="coerce")
        df["cliques"]      = pd.to_numeric(df["cliques"],      errors="coerce")
        df["conversoes"]   = pd.to_numeric(df["conversoes"],   errors="coerce")

        return df.dropna(subset=["data", "investimento"])

    except Exception as exc:
        st.error(f"❌ Erro ao processar arquivo: {exc}")
        return None


# =============================================================
# 📐 MÓDULO 2 — MÉTRICAS
#     Cálculo dos KPIs essenciais de marketing digital
# =============================================================

def calcular_metricas(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs de marketing a partir do DataFrame consolidado.

    Fórmulas aplicadas:
        ROAS             = Receita Total / Investimento Total
        CPA              = Investimento Total / Total de Conversões
        CPC              = Investimento Total / Total de Cliques
        CTR              = (Cliques / Impressões) × 100
        Taxa de Conversão = (Conversões / Cliques) × 100

    Returns:
        dict com métricas gerais + DataFrame 'por_campanha'
    """
    inv  = df["investimento"].sum()
    rec  = df["receita"].sum()
    cli  = df["cliques"].sum()
    imp  = df["impressoes"].sum()
    conv = df["conversoes"].sum()

    gerais = {
        "investimento_total": inv,
        "receita_total":      rec,
        "lucro_liquido":      rec - inv,
        "total_cliques":      int(cli),
        "total_impressoes":   int(imp),
        "total_conversoes":   int(conv),
        "roas":               round(rec / inv,  2) if inv  > 0 else 0.0,
        "cpa":                round(inv / conv, 2) if conv > 0 else 0.0,
        "cpc":                round(inv / cli,  2) if cli  > 0 else 0.0,
        "ctr":                round((cli / imp) * 100,  2) if imp  > 0 else 0.0,
        "taxa_conversao":     round((conv / cli) * 100, 2) if cli  > 0 else 0.0,
    }

    # Agrupamento granular por campanha e canal
    por_campanha = (
        df.groupby(["campanha", "canal"])
        .agg(
            investimento=("investimento", "sum"),
            receita     =("receita",      "sum"),
            conversoes  =("conversoes",   "sum"),
            cliques     =("cliques",      "sum"),
            impressoes  =("impressoes",   "sum"),
        )
        .reset_index()
    )
    por_campanha["roas"] = (
        por_campanha["receita"] / por_campanha["investimento"]
    ).round(2)
    por_campanha["cpa"] = (
        por_campanha["investimento"]
        / por_campanha["conversoes"].replace(0, pd.NA)
    ).round(2)
    por_campanha["ctr"] = (
        (por_campanha["cliques"] / por_campanha["impressoes"]) * 100
    ).round(2)

    return {**gerais, "por_campanha": por_campanha}


# =============================================================
# 🤖 MÓDULO 3 — GEMINI AI
#     Prompt especializado + chamada à API
# =============================================================

# System prompt que força o modelo a agir como Diretor de Growth
_SYSTEM_PROMPT = """
Você é um Diretor de Growth e Performance com 15 anos de experiência gerenciando \
contas de mídia paga com orçamentos acima de R$ 1 milhão/mês para e-commerces e \
empresas de serviço no Brasil.

Sua especialidade é ler dados de campanhas e transformar números em decisões de \
negócio claras, diretas e acionáveis. Você não tolera análises genéricas.

═══ REGRAS ABSOLUTAS (sem exceção) ═══
1. Seja DIRETO e EXECUTIVO. Zero enrolação ou introduções genéricas.
2. Cada afirmação deve ser ancorada em UM número real dos dados fornecidos.
3. Identifique sempre a campanha com MELHOR e PIOR ROAS e justifique tecnicamente.
4. O plano de ação deve ser implementável ESTA SEMANA, com métricas-alvo concretas.
5. Tom: consultor sênior conversando com gestor de tráfego experiente — \
não explique o que é ROAS ou CPA.
6. Limite RÍGIDO: máximo 380 palavras no total.
7. Responda EXCLUSIVAMENTE com o bloco Markdown abaixo, \
sem nenhum texto antes ou depois:

---
### 🔍 Diagnóstico
[2–3 frases sobre o estado geral da conta. Cite o ROAS atual vs. benchmark \
do setor (3x). Aponte o principal gargalo que está drenando budget sem retorno.]

### ✅ Onde o Dinheiro Está Sendo Bem Gasto
[Cite a campanha/canal com melhor ROAS ou menor CPA, com o valor exato. \
Explique em 1–2 frases a hipótese técnica por trás dessa eficiência — \
intenção de busca, estágio do funil, temperatura do público etc.]

### ⚡ Plano de Ação para Esta Semana
- **Ação 1 — Corte imediato:** [Campanha com pior ROAS → ação específica, \
ex: "reduzir budget em 35%" ou "pausar público lookalike frio X"]
- **Ação 2 — Escalar o que funciona:** [Campanha top → quanto aumentar o \
budget em % e qual métrica monitorar diariamente]
- **Ação 3 — Otimização de qualidade:** [Ajuste de copy, audience ou \
estratégia de lance baseado no CTR/taxa de conversão atual]
---
"""


def _build_prompt(metricas: dict) -> str:
    """Monta o prompt com os dados de performance — compartilhado entre Gemini e Groq."""
    df_camp = (
        metricas["por_campanha"][[
            "campanha", "canal", "investimento", "receita",
            "conversoes", "cliques", "roas", "cpa", "ctr",
        ]]
        .sort_values("roas", ascending=False)
    )
    tabela_str = df_camp.to_string(index=False, float_format="{:.2f}".format)

    return f"""
Analise os dados de performance de mídia paga dos últimos 30 dias e gere o \
relatório diagnóstico:

═══ MÉTRICAS CONSOLIDADAS DO PERÍODO ═══
• Investimento Total  : R$ {metricas['investimento_total']:>10,.2f}
• Receita Total       : R$ {metricas['receita_total']:>10,.2f}
• Lucro Líquido       : R$ {metricas['lucro_liquido']:>10,.2f}
• ROAS Consolidado    : {metricas['roas']:.2f}×
• CPA Médio           : R$ {metricas['cpa']:,.2f}
• CPC Médio           : R$ {metricas['cpc']:,.2f}
• CTR Médio           : {metricas['ctr']:.2f}%
• Taxa de Conversão   : {metricas['taxa_conversao']:.2f}%
• Total de Conversões : {metricas['total_conversoes']:,}
• Total de Cliques    : {metricas['total_cliques']:,}

═══ DETALHAMENTO POR CAMPANHA ═══
{tabela_str}

Gere o relatório agora.
"""


def _chamar_gemini(prompt: str, api_key: str) -> str:
    """Chama a API do Google Gemini. Lança exceção em caso de erro."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=0.35,
            max_output_tokens=1024,
        ),
    )
    response = model.generate_content(prompt)
    return response.text


def _chamar_groq(prompt: str, groq_key: str) -> str:
    """
    Chama a API do Groq usando Llama 3.3 70B como fallback gratuito.
    Groq oferece 14.400 requisições/dia no plano free — muito mais generoso que o Gemini.
    """
    from groq import Groq

    client = Groq(api_key=groq_key)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.35,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def gerar_diagnostico_ia(metricas: dict, gemini_key: str, groq_key: str = "") -> str:
    """
    Orquestra o diagnóstico com fallback automático:
      1. Tenta Gemini (mais avançado)
      2. Se cota atingida (429) → cai para Groq automaticamente
      3. Se nenhuma key disponível → instrução ao usuário

    Args:
        metricas   (dict): KPIs calculados por calcular_metricas()
        gemini_key (str):  Chave da API do Google AI Studio (pode ser vazia)
        groq_key   (str):  Chave da API do Groq (pode ser vazia)

    Returns:
        str: Relatório em Markdown, com indicação de qual modelo foi usado
    """
    prompt = _build_prompt(metricas)

    # ── Tenta Gemini ──────────────────────────────────────────
    if gemini_key:
        try:
            resultado = _chamar_gemini(prompt, gemini_key)
            return f"*Análise gerada por **Gemini 2.0 Flash** (Google AI)*\n\n---\n\n{resultado}"
        except Exception as exc:
            msg = str(exc).lower()
            eh_cota = any(k in msg for k in ["429", "quota", "limit", "resource_exhausted", "toomanyrequests"])
            eh_key  = any(k in msg for k in ["api_key", "invalid", "permission", "unauthenticated"])

            if eh_key:
                return "❌ **Gemini: API Key inválida.** Verifique a chave no Google AI Studio."

            if eh_cota and groq_key:
                # ── Fallback automático para Groq ──────────────
                st.toast("⚠️ Gemini com limite atingido — usando Groq como fallback!", icon="🔄")
                try:
                    resultado = _chamar_groq(prompt, groq_key)
                    return (
                        f"*Análise gerada por **Llama 3.3 70B via Groq** "
                        f"(fallback automático — Gemini com cota atingida)*\n\n---\n\n{resultado}"
                    )
                except Exception as groq_exc:
                    return f"❌ **Ambas as APIs falharam.**\n- Gemini: `{exc}`\n- Groq: `{groq_exc}`"

            if eh_cota:
                return (
                    "⚠️ **Cota do Gemini atingida.**\n\n"
                    "Configure uma **GROQ_API_KEY** nos Secrets do Streamlit Cloud para "
                    "ativar o fallback automático gratuito (14.400 req/dia).\n\n"
                    "> Acesse **console.groq.com** → API Keys → Create API Key"
                )

            return f"❌ **Erro inesperado no Gemini:**\n```\n{exc}\n```"

    # ── Usa Groq diretamente se não tiver Gemini ──────────────
    if groq_key:
        try:
            resultado = _chamar_groq(prompt, groq_key)
            return f"*Análise gerada por **Llama 3.3 70B via Groq***\n\n---\n\n{resultado}"
        except Exception as exc:
            return f"❌ **Erro no Groq:** `{exc}`"

    return "❌ Configure pelo menos uma API Key (Gemini ou Groq) na sidebar."


# =============================================================
# 📈 MÓDULO 4 — GRÁFICOS
#     Visualizações interativas com Plotly Graph Objects
# =============================================================

def grafico_investimento_receita(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de linha dupla: Investimento vs Receita ao longo dos 30 dias.
    Inclui área preenchida sob a linha de receita para indicar lucro.
    """
    df_diario = (
        df.groupby("data")
        .agg(investimento=("investimento", "sum"), receita=("receita", "sum"))
        .reset_index()
        .sort_values("data")
    )

    fig = go.Figure()

    # Receita — área preenchida (indica o "ganho")
    fig.add_trace(go.Scatter(
        x=df_diario["data"],
        y=df_diario["receita"],
        name="💰 Receita",
        mode="lines+markers",
        line=dict(color="#10B981", width=2.5),
        marker=dict(size=4),
        fill="tozeroy",
        fillcolor="rgba(16,185,129,0.09)",
        hovertemplate="Receita: R$ %{y:,.2f}<extra></extra>",
    ))

    # Investimento — linha tracejada (indica o "custo")
    fig.add_trace(go.Scatter(
        x=df_diario["data"],
        y=df_diario["investimento"],
        name="💸 Investimento",
        mode="lines+markers",
        line=dict(color="#EF4444", width=2.5, dash="dot"),
        marker=dict(size=4),
        hovertemplate="Investimento: R$ %{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        title="📈 Investimento vs Receita — Últimos 30 Dias",
        height=370,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=55, b=0),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(156,163,175,0.25)",
        title_text="",
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(156,163,175,0.25)",
        tickprefix="R$ ", title_text="",
    )
    return fig


def grafico_roas_campanhas(metricas: dict, meta_roas: float = 3.0) -> go.Figure:
    """
    Gráfico de barras horizontais com ROAS por campanha.
    Barras verdes = acima da meta 3×. Barras vermelhas = abaixo.
    Linha pontilhada indica a meta de ROAS = 3×.
    """
    df = metricas["por_campanha"].sort_values("roas")
    cores = ["#EF4444" if r < 3.0 else "#10B981" for r in df["roas"]]

    fig = go.Figure(go.Bar(
        x=df["roas"],
        y=df["campanha"],
        orientation="h",
        marker_color=cores,
        text=[f"{r:.2f}×" for r in df["roas"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>ROAS: %{x:.2f}×<extra></extra>",
    ))

    # Linha de meta (ROAS = 3×)
    fig.add_vline(
        x=3.0,
        line_dash="dash",
        line_color="#F59E0B",
        line_width=1.8,
        annotation_text="Meta 3×",
        annotation_position="top right",
        annotation_font_color="#F59E0B",
    )

    fig.update_layout(
        title="🎯 ROAS por Campanha",
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=65, t=50, b=0),
        showlegend=False,
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(156,163,175,0.25)", title_text="ROAS (×)"
    )
    fig.update_yaxes(showgrid=False, title_text="")
    return fig


# =============================================================
# 🖥️  MÓDULO 5 — INTERFACE STREAMLIT (Design Moderno)
#     Sidebar, header, KPI cards, gráficos e diagnóstico de IA
# =============================================================

def render_sidebar() -> tuple:
    """Renderiza sidebar e retorna (url_planilha, arquivo_upload, api_key)."""
    with st.sidebar:
        # ── Logo ─────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🚀</div>
            <div class="sidebar-logo-text">
                <div class="sidebar-logo-title">AdPerform AI</div>
                <div class="sidebar-logo-sub">Performance Intelligence</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Fonte de Dados ───────────────────────────────────────
        st.markdown('<div class="sidebar-section">📋 Fonte de Dados</div>', unsafe_allow_html=True)
        fonte_opcao = st.radio(
            "Origem dos dados:",
            ["📊 Dados Simulados", "📁 Upload CSV / Excel", "🔗 Google Sheets"],
            index=0,
            label_visibility="collapsed",
        )

        url_planilha   = ""
        arquivo_upload = None

        if fonte_opcao == "📁 Upload CSV / Excel":
            arquivo_upload = st.file_uploader(
                "Arquivo",
                type=["csv", "xlsx", "xls"],
                help="Colunas obrigatórias: data | campanha | canal | investimento | impressoes | cliques | conversoes | receita",
                label_visibility="collapsed",
            )
            st.download_button(
                label="⬇️ Baixar template Excel",
                data=gerar_template_excel(),
                file_name="template_adperform_ai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        elif fonte_opcao == "🔗 Google Sheets":
            url_planilha = st.text_input(
                "URL CSV",
                placeholder="https://docs.google.com/spreadsheets/...",
                help="Arquivo → Publicar na Web → Formato CSV → Publicar → Copie o link",
                label_visibility="collapsed",
            )
            if url_planilha and "format=csv" not in url_planilha:
                st.caption("💡 URL deve terminar com `format=csv`")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gemini AI ────────────────────────────────────────────
        st.markdown('<div class="sidebar-section">🤖 Gemini AI</div>', unsafe_allow_html=True)
        api_key = ""

        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.markdown("""
            <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
                        border-radius:8px;padding:8px 12px;font-size:0.75rem;color:#6EE7B7;
                        display:flex;align-items:center;gap:6px;">
                🔐 API Key ativa e segura
            </div>
            """, unsafe_allow_html=True)
        except (KeyError, FileNotFoundError):
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="AIzaSy...",
                label_visibility="collapsed",
                help="Obtenha em: aistudio.google.com/app/apikey",
            )
            if not api_key:
                st.markdown("""
                <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.22);
                            border-radius:8px;padding:8px 12px;font-size:0.73rem;color:#FCD34D;">
                    ⚠️ Configure a API Key para ativar a IA
                </div>
                """, unsafe_allow_html=True)

        # ── Groq API Key (fallback gratuito) ────────────────────
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.70rem;color:#64748B;font-weight:600;
                    letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;">
            🦙 Groq AI · Fallback Gratuito
        </div>
        <div style="font-size:0.68rem;color:#475569;margin-bottom:8px;">
            Ativa automaticamente se o Gemini atingir o limite.
            <a href="https://console.groq.com" target="_blank"
               style="color:#3B82F6;">Obter chave grátis →</a>
        </div>
        """, unsafe_allow_html=True)

        groq_key = ""
        try:
            groq_key = st.secrets["GROQ_API_KEY"]
            st.markdown("""
            <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
                        border-radius:8px;padding:8px 12px;font-size:0.75rem;color:#6EE7B7;
                        display:flex;align-items:center;gap:6px;">
                🦙 Groq Key ativa — fallback pronto
            </div>
            """, unsafe_allow_html=True)
        except (KeyError, FileNotFoundError):
            groq_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                label_visibility="collapsed",
                help="Obtenha gratuitamente em: console.groq.com",
            )
            if groq_key:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                            border-radius:8px;padding:8px 12px;font-size:0.73rem;color:#6EE7B7;">
                    🦙 Groq configurado — fallback ativo
                </div>
                """, unsafe_allow_html=True)

        # ── Metas da Conta ───────────────────────────────────────
        st.divider()
        st.markdown("""
        <div style="font-size:0.70rem;color:#64748B;font-weight:600;
                    letter-spacing:0.06em;text-transform:uppercase;margin-bottom:8px;">
            🎯 Metas da Conta
        </div>
        """, unsafe_allow_html=True)

        meta_roas = st.number_input(
            "Meta de ROAS",
            min_value=0.5, max_value=50.0, value=3.0, step=0.5,
            help="Meta de retorno sobre investimento em anúncios. Padrão de mercado: 3×",
        )
        meta_cpa = st.number_input(
            "Meta de CPA (R$)",
            min_value=1.0, max_value=5000.0, value=60.0, step=5.0,
            help="Custo máximo aceitável por aquisição/conversão no seu nicho",
        )

        # ── Rodapé ───────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="border-top:1px solid rgba(59,130,246,0.1);padding-top:12px;">
            <div style="font-size:0.65rem;color:#334155;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">v2.0.0 · AdPerform AI</div>
            <div style="font-size:0.63rem;color:#1E293B;margin-top:3px;">Gemini + Groq · Streamlit</div>
        </div>
        """, unsafe_allow_html=True)

    return url_planilha, arquivo_upload, api_key, groq_key, meta_roas, meta_cpa




def grafico_distribuicao_investimento(df: pd.DataFrame, por: str = "canal") -> go.Figure:
    """
    Gráfico donut mostrando % do investimento total por canal ou campanha.
    por = "canal" | "campanha"
    """
    df_group = (
        df.groupby(por)["investimento"]
        .sum()
        .reset_index()
        .sort_values("investimento", ascending=False)
    )

    cores = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

    fig = go.Figure(go.Pie(
        labels=df_group[por],
        values=df_group["investimento"],
        hole=0.65,
        marker=dict(colors=cores[:len(df_group)],
                    line=dict(color="#080E1C", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="#F1F5F9"),
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
    ))

    titulo = "por Canal" if por == "canal" else "por Campanha"
    fig.update_layout(
        title=f"🍩 Distribuição de Investimento {titulo}",
        height=310,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#9CA3AF", size=10),
                    bgcolor="rgba(0,0,0,0)",
                    orientation="v", x=1.0, y=0.5),
        margin=dict(l=0, r=10, t=50, b=0),
        annotations=[dict(
            text=f"<b>R$<br>{df_group['investimento'].sum()/1000:.1f}k</b>",
            x=0.5, y=0.5, font=dict(size=14, color="#F1F5F9"),
            showarrow=False,
        )],
    )
    return fig


def grafico_eficiencia_temporal(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de linha dupla: evolução de CPC e CTR ao longo do tempo.
    Usa eixo Y duplo pois as escalas são muito diferentes.
    """
    df_diario = (
        df.groupby("data")
        .agg(investimento=("investimento","sum"),
             cliques=("cliques","sum"),
             impressoes=("impressoes","sum"))
        .reset_index()
        .sort_values("data")
    )
    df_diario["cpc"] = (df_diario["investimento"] / df_diario["cliques"].replace(0, pd.NA)).round(2)
    df_diario["ctr"] = ((df_diario["cliques"] / df_diario["impressoes"].replace(0, pd.NA)) * 100).round(2)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_diario["data"], y=df_diario["cpc"],
        name="CPC (R$)", mode="lines+markers",
        line=dict(color="#F59E0B", width=2.5),
        marker=dict(size=4),
        yaxis="y1",
        hovertemplate="CPC: R$ %{y:.2f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_diario["data"], y=df_diario["ctr"],
        name="CTR (%)", mode="lines+markers",
        line=dict(color="#8B5CF6", width=2.5, dash="dot"),
        marker=dict(size=4),
        yaxis="y2",
        hovertemplate="CTR: %{y:.2f}%%<extra></extra>",
    ))

    fig.update_layout(
        title="📉 Evolução de CPC e CTR",
        height=310,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                    font=dict(color="#9CA3AF")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=60, t=55, b=0),
        yaxis=dict(title="CPC (R$)", tickprefix="R$ ",
                   gridcolor="rgba(156,163,175,0.15)",
                   color="#F59E0B"),
        yaxis2=dict(title="CTR (%)", ticksuffix="%",
                    overlaying="y", side="right",
                    gridcolor="rgba(156,163,175,0.08)",
                    color="#8B5CF6"),
    )
    return fig

def render_header(fonte: str, data_ini: str, data_fim: str, api_key: str) -> None:
    """Renderiza o banner de cabeçalho com badges de status."""
    ai_badge = (
        '<span class="badge badge-green">✅ Gemini AI Ativo</span>'
        if api_key else
        '<span class="badge badge-yellow">⚠️ IA não configurada</span>'
    )
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-title">🚀 AdPerform AI</div>
        <div class="dash-sub">Dashboard de Performance de Vendas com Diagnóstico Automatizado por IA</div>
        <div class="dash-badges">
            <span class="badge badge-blue">📊 Gestores de Tráfego</span>
            <span class="badge badge-green">🔒 Dados Protegidos</span>
            {ai_badge}
            <span class="badge badge-blue">📅 {data_ini} → {data_fim}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpis_cards(metricas: dict, deltas: dict = {}, df_completo: object = None, periodo_dias: int = 30) -> None:
    """
    Renderiza 5 KPI cards com hover effect, barra gradiente no topo
    e comparativo vs período anterior (quando deltas disponíveis).

    Regra de cor dos deltas:
      ROAS, CTR, Conv Rate → positivo = verde (melhorou)
      CPA, CPC             → negativo = verde (custo caiu = bom)
    """
    roas    = metricas["roas"]
    ok_roas = roas >= 3.0

    # Calcula quantos dias a mais são necessários para ter comparativo
    dias_disponiveis = int((df_completo["data"].max() - df_completo["data"].min()).days) + 1 if df_completo is not None else 0
    precisam = periodo_dias * 2

    def fmt_delta(key: str, inverso: bool = False) -> tuple[str, str]:
        """Formata o delta e retorna (texto, classe CSS)."""
        val = deltas.get(key)
        if val is None:
            if dias_disponiveis < precisam:
                faltam = precisam - dias_disponiveis
                return f"📅 +{faltam} dias para comparar", "kpi-delta-neu"
            return "— período ant. sem dados", "kpi-delta-neu"
        bom = (val < 0) if inverso else (val > 0)
        sinal = "▲" if val > 0 else "▼"
        cls   = "kpi-delta-pos" if bom else "kpi-delta-neg"
        return f"{sinal} {abs(val):.1f}% vs período ant.", cls

    # Se não tiver deltas, usa texto descritivo padrão
    if deltas:
        d_roas_txt,  d_roas_cls  = fmt_delta("roas")
        d_cpa_txt,   d_cpa_cls   = fmt_delta("cpa",  inverso=True)
        d_cpc_txt,   d_cpc_cls   = fmt_delta("cpc",  inverso=True)
        d_ctr_txt,   d_ctr_cls   = fmt_delta("ctr")
        d_conv_txt,  d_conv_cls  = fmt_delta("taxa_conversao")
    else:
        d_roas_txt  = "✅ Acima da meta" if ok_roas else "⚠️ Abaixo da meta (3×)"
        d_roas_cls  = "kpi-delta-pos" if ok_roas else "kpi-delta-neg"
        d_cpa_txt   = d_cpc_txt = d_ctr_txt = d_conv_txt = "Custo/Aquisição Custo/Clique Click-Through Taxa Conv.".split()[0]
        d_cpa_cls   = d_cpc_cls = d_ctr_cls = d_conv_cls = "kpi-delta-neu"
        d_cpa_txt   = "Custo por Aquisição"
        d_cpc_txt   = "Custo por Clique"
        d_ctr_txt   = "Click-Through Rate"
        d_conv_txt  = "Taxa de Conversão"

    kpis = [
        ("ROAS",       f"{roas:.2f}×",                      d_roas_cls,  d_roas_txt),
        ("CPA",        f"R$ {metricas['cpa']:,.2f}",        d_cpa_cls,   d_cpa_txt),
        ("CPC",        f"R$ {metricas['cpc']:,.2f}",        d_cpc_cls,   d_cpc_txt),
        ("CTR",        f"{metricas['ctr']:.2f}%",           d_ctr_cls,   d_ctr_txt),
        ("CONV. RATE", f"{metricas['taxa_conversao']:.2f}%",d_conv_cls,  d_conv_txt),
    ]

    cols = st.columns(5)
    for col, (label, value, delta_cls, delta_txt) in zip(cols, kpis):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_cls}">{delta_txt}</div>
        </div>
        """, unsafe_allow_html=True)


def render_resumo_financeiro(metricas: dict) -> None:
    """Renderiza 3 finance cards com investimento, receita e lucro."""
    lucro       = metricas["lucro_liquido"]
    lucro_class = "green" if lucro > 0 else "red"
    lucro_icon  = "📈" if lucro > 0 else "📉"

    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "💸 INVESTIMENTO TOTAL",
         f"R$ {metricas['investimento_total']:,.2f}", "",
         f"{metricas['total_cliques']:,} cliques gerados"),
        (c2, "💵 RECEITA GERADA",
         f"R$ {metricas['receita_total']:,.2f}", "green",
         f"{metricas['total_conversoes']:,} conversões"),
        (c3, f"{lucro_icon} LUCRO LÍQUIDO",
         f"R$ {lucro:,.2f}", lucro_class,
         "Receita − Investimento"),
    ]
    for col, label, value, val_class, sub in cards:
        col.markdown(f"""
        <div class="fin-card">
            <div class="fin-label">{label}</div>
            <div class="fin-value {val_class}">{value}</div>
            <div class="fin-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


def render_tabela_campanhas(metricas: dict) -> None:
    """
    Tabela de performance por campanha com cores semânticas.
    Usa .map() em vez de background_gradient — sem dependência de matplotlib.
    """
    df_exib = metricas["por_campanha"].copy()
    df_exib = df_exib.sort_values("roas", ascending=False)
    df_exib.columns = [
        "Campanha", "Canal", "Invest. (R$)", "Receita (R$)",
        "Conversões", "Cliques", "Impressões", "ROAS", "CPA (R$)", "CTR (%)",
    ]

    def cor_roas(val):
        try:
            v = float(str(val).replace("×", "").strip())
            if v >= 4.0:   return "color: #10B981; font-weight: 700"
            elif v >= 3.0: return "color: #6EE7B7; font-weight: 600"
            elif v >= 2.0: return "color: #F59E0B; font-weight: 600"
            else:          return "color: #EF4444; font-weight: 700"
        except Exception:  return ""

    def cor_cpa(val):
        try:
            v = float(str(val).replace("R$", "").replace(",", "").strip())
            if v <= 30:    return "color: #10B981; font-weight: 600"
            elif v <= 60:  return "color: #F59E0B; font-weight: 600"
            else:          return "color: #EF4444; font-weight: 700"
        except Exception:  return ""

    st.dataframe(
        df_exib.style
            .format({
                "Invest. (R$)": "R$ {:,.2f}",
                "Receita (R$)": "R$ {:,.2f}",
                "CPA (R$)":     "R$ {:,.2f}",
                "ROAS":         "{:.2f}×",
                "CTR (%)":      "{:.2f}%",
            })
            .map(cor_roas, subset=["ROAS"])
            .map(cor_cpa,  subset=["CPA (R$)"]),
        use_container_width=True,
        hide_index=True,
        height=230,
    )


# =============================================================
# 🎬 MAIN — Orquestra o app completo
# =============================================================


# =============================================================
# 🔎 MÓDULO 6 — FILTROS
# =============================================================

def render_filtros(df: pd.DataFrame) -> tuple[int, list, list]:
    """
    Renderiza controles de filtro e retorna (periodo_dias, canais, campanhas).
    Aparece logo abaixo do header — linha de controles compacta.
    """
    canais_disponiveis    = sorted(df["canal"].unique().tolist())
    campanhas_disponiveis = sorted(df["campanha"].unique().tolist())

    st.markdown('<div class="sec-title">🔎 Filtros</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        periodo_opcao = st.radio(
            "Período de análise",
            ["7 dias", "14 dias", "30 dias"],
            index=2,
            horizontal=True,
            help="Define o período atual. O período anterior equivalente é calculado automaticamente para o comparativo.",
        )
        periodo_dias = int(periodo_opcao.split()[0])

    with col2:
        canais_sel = st.multiselect(
            "Canal",
            canais_disponiveis,
            default=[],
            placeholder="Todos os canais",
        )

    with col3:
        campanhas_sel = st.multiselect(
            "Campanha",
            campanhas_disponiveis,
            default=[],
            placeholder="Todas as campanhas",
        )

    st.markdown('<hr style="border-color:rgba(59,130,246,0.08);margin:8px 0 16px;">', unsafe_allow_html=True)
    return periodo_dias, canais_sel, campanhas_sel


def aplicar_filtros(df: pd.DataFrame, periodo_dias: int,
                    canais: list, campanhas: list) -> pd.DataFrame:
    """
    Filtra o DataFrame pelo período, canais e campanhas selecionados.
    Sempre usa os dias mais recentes como período atual.
    """
    data_fim = df["data"].max()
    data_ini = data_fim - timedelta(days=periodo_dias - 1)
    df_f = df[df["data"] >= data_ini].copy()

    if canais:
        df_f = df_f[df_f["canal"].isin(canais)]
    if campanhas:
        df_f = df_f[df_f["campanha"].isin(campanhas)]

    return df_f


def calcular_periodo_anterior(df: pd.DataFrame, periodo_dias: int,
                               canais: list, campanhas: list) -> Optional[dict]:
    """
    Calcula métricas do período imediatamente anterior ao atual.
    Retorna None se não houver dados suficientes.
    """
    data_fim        = df["data"].max()
    data_ini_atual  = data_fim - timedelta(days=periodo_dias - 1)
    data_fim_ant    = data_ini_atual - timedelta(days=1)
    data_ini_ant    = data_fim_ant - timedelta(days=periodo_dias - 1)

    df_ant = df[(df["data"] >= data_ini_ant) & (df["data"] <= data_fim_ant)].copy()
    if canais:
        df_ant = df_ant[df_ant["canal"].isin(canais)]
    if campanhas:
        df_ant = df_ant[df_ant["campanha"].isin(campanhas)]

    if df_ant.empty:
        return None

    return calcular_metricas(df_ant)


def calcular_deltas(atual: dict, anterior: Optional[dict]) -> dict:
    """
    Calcula variações percentuais entre período atual e anterior.
    Retorna dict vazio se anterior for None.

    Sinal do delta:
      ROAS, CTR, Taxa Conv → positivo é bom (verde)
      CPA, CPC              → negativo é bom (verde — custo caiu)
    """
    if anterior is None:
        return {}

    deltas = {}
    for key in ["roas", "cpa", "cpc", "ctr", "taxa_conversao",
                "investimento_total", "receita_total", "lucro_liquido"]:
        val_a = atual.get(key, 0) or 0
        val_p = anterior.get(key, 0) or 0
        if val_p != 0:
            deltas[key] = round(((val_a - val_p) / abs(val_p)) * 100, 1)
        else:
            deltas[key] = None
    return deltas


# =============================================================
# 🚨 MÓDULO 7 — ALERTAS AUTOMÁTICOS
# =============================================================

def render_alertas(metricas: dict, meta_roas: float = 3.0, meta_cpa: float = 60.0) -> None:
    """
    Exibe banners de alerta automáticos baseados em thresholds de KPIs.
    Crítico (vermelho): requer ação imediata.
    Atenção (amarelo):  monitorar de perto.
    """
    alertas: list[tuple[str, str, str]] = []

    roas = metricas["roas"]
    ctr  = metricas["ctr"]
    tconv = metricas["taxa_conversao"]

    # ── Nível de conta ────────────────────────────────────────
    roas_minimo = round(meta_roas * 0.67, 2)  # 67% da meta = zona crítica
    if roas < roas_minimo:
        alertas.append(("🔴 CRÍTICO",
            f"ROAS consolidado em {roas:.2f}× — abaixo do mínimo aceitável ({roas_minimo:.1f}×). "
            "Pausar campanhas deficitárias imediatamente.", "red"))
    elif roas < meta_roas:
        alertas.append(("🟡 ATENÇÃO",
            f"ROAS em {roas:.2f}× — abaixo da sua meta de {meta_roas:.1f}×. "
            "Redistribuir budget para campanhas mais eficientes.", "yellow"))

    if ctr < 1.0:
        alertas.append(("🟡 ATENÇÃO",
            f"CTR médio de {ctr:.2f}% — muito baixo. "
            "Testar novos criativos e revisar segmentações.", "yellow"))

    if tconv < 1.5:
        alertas.append(("🟡 ATENÇÃO",
            f"Taxa de conversão de {tconv:.2f}% — abaixo do esperado. "
            "Revisar landing pages e ofertas das campanhas.", "yellow"))

    # ── Nível de campanha ─────────────────────────────────────
    for _, row in metricas["por_campanha"].iterrows():
        roas_critico = round(meta_roas * 0.50, 2)
        if pd.notna(row["roas"]) and row["roas"] < roas_critico:
            alertas.append(("🔴 CRÍTICO",
                f"Campanha '{row['campanha']}' com ROAS de {row['roas']:.2f}× — "
                f"abaixo de {roas_critico:.1f}× (50% da sua meta). Pausar ou reestruturar.", "red"))
        elif pd.notna(row.get('cpa')) and row['cpa'] > meta_cpa * 1.5:
            alertas.append(("🟡 ATENÇÃO",
                f"Campanha '{row['campanha']}' com CPA de R$ {row['cpa']:.2f} — "
                f"{((row['cpa']/meta_cpa)-1)*100:.0f}% acima da sua meta (R$ {meta_cpa:.0f}).", "yellow"))

    if not alertas:
        return  # tudo dentro do esperado — não exibe nada

    st.markdown('<div class="sec-title">🚨 Alertas Automáticos</div>', unsafe_allow_html=True)
    for nivel, msg, cor in alertas:
        bg     = "rgba(239,68,68,0.08)"  if cor == "red" else "rgba(245,158,11,0.08)"
        border = "rgba(239,68,68,0.28)"  if cor == "red" else "rgba(245,158,11,0.28)"
        color  = "#FCA5A5"               if cor == "red" else "#FCD34D"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:10px;
                    padding:11px 16px;margin-bottom:8px;font-size:0.82rem;color:{color};
                    display:flex;align-items:flex-start;gap:10px;">
            <span style="font-weight:700;white-space:nowrap;">{nivel}</span>
            <span>{msg}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# =============================================================
# 📄 MÓDULO 8 — EXPORTAÇÃO PDF
# =============================================================

def gerar_pdf(metricas: dict, diagnostico_txt: str,
              periodo_label: str, fonte: str) -> bytes:
    """
    Gera um relatório PDF profissional com KPIs, tabela de campanhas
    e diagnóstico da IA.

    Usa fpdf2 — sem dependências de sistema (compatível com Streamlit Cloud).
    Emojis e caracteres não-Latin são removidos automaticamente.
    """
    import re
    from fpdf import FPDF

    def limpar(texto: str) -> str:
        """
        Remove TUDO fora do Latin-1 (emojis, Unicode especial) e markdown.
        Usa encode/decode — método mais confiável que regex para fpdf2 + Helvetica.
        """
        if not isinstance(texto, str):
            texto = str(texto)
        # encode para Latin-1, ignorando tudo que não suportar (emojis, —, ×, etc.)
        texto = texto.encode("latin-1", errors="ignore").decode("latin-1")
        texto = re.sub(r"[#*`_>~]", "", texto)      # remove markdown
        texto = re.sub(r"\n{3,}", "\n\n", texto)    # colapsa linhas em branco
        texto = texto.replace("->", "->")           # normaliza seta
        return texto.strip()

    # Limpa TODAS as strings externas antes de entrar no PDF
    fonte_pdf         = limpar(fonte)
    periodo_label_pdf = limpar(periodo_label)
    diagnostico_pdf   = limpar(diagnostico_txt) if diagnostico_txt else ""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Cabeçalho ────────────────────────────────────────────
    pdf.set_fill_color(8, 14, 28)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(12, 10)
    pdf.cell(0, 10, "AdPerform AI", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(12, 23)
    pdf.cell(0, 6, f"Relatorio de Performance | {periodo_label_pdf} | {fonte_pdf}", ln=True)
    pdf.set_xy(12, 31)
    pdf.set_text_color(100, 150, 220)
    pdf.cell(0, 6, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

    # ── KPIs ──────────────────────────────────────────────────
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(10, 52)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "KPIs do Periodo", ln=True)
    pdf.set_font("Helvetica", "", 10)

    kpis_pdf = [
        ("ROAS",              f"{metricas['roas']:.2f}x"),
        ("CPA (Custo/Conv.)", f"R$ {metricas['cpa']:,.2f}"),
        ("CPC (Custo/Clique)",f"R$ {metricas['cpc']:,.2f}"),
        ("CTR",               f"{metricas['ctr']:.2f}%"),
        ("Taxa de Conversao", f"{metricas['taxa_conversao']:.2f}%"),
        ("Investimento Total", f"R$ {metricas['investimento_total']:,.2f}"),
        ("Receita Total",     f"R$ {metricas['receita_total']:,.2f}"),
        ("Lucro Liquido",     f"R$ {metricas['lucro_liquido']:,.2f}"),
        ("Total Conversoes",  f"{metricas['total_conversoes']:,}"),
        ("Total Cliques",     f"{metricas['total_cliques']:,}"),
    ]

    fill = False
    for label, value in kpis_pdf:
        if fill:
            pdf.set_fill_color(240, 244, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 7, label, border=0, fill=fill)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 7, value, border=0, fill=fill, ln=True)
        fill = not fill

    # ── Tabela de Campanhas ───────────────────────────────────
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Performance por Campanha", ln=True)

    headers = ["Campanha", "Canal", "Invest.", "Receita", "Conv.", "ROAS", "CPA"]
    widths  = [60, 28, 22, 22, 14, 18, 20]
    pdf.set_fill_color(8, 14, 28)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=0, fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for _, row in metricas["por_campanha"].sort_values("roas", ascending=False).iterrows():
        if fill:
            pdf.set_fill_color(240, 244, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        cpa_val = f"R$ {row['cpa']:,.2f}" if pd.notna(row["cpa"]) else "N/A"
        vals = [
            limpar(str(row["campanha"]))[:30],
            limpar(str(row["canal"])),
            f"R$ {row['investimento']:,.0f}",
            f"R$ {row['receita']:,.0f}",
            str(int(row["conversoes"])),
            f"{row['roas']:.2f}x",
            cpa_val,
        ]
        for v, w in zip(vals, widths):
            pdf.cell(w, 6, v, border=0, fill=True)
        pdf.ln()
        fill = not fill

    # ── Diagnóstico da IA ─────────────────────────────────────
    if diagnostico_txt:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Diagnostico Executivo por IA", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5.5, diagnostico_pdf)

    # ── Rodapé ───────────────────────────────────────────────
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8,
        f"AdPerform AI | Relatorio gerado automaticamente | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        align="C"
    )

    return bytes(pdf.output())



# =============================================================
# 🏆 MÓDULO 9 — SCORE DE SAÚDE DA CONTA
# =============================================================

def calcular_health_score(metricas: dict, meta_roas: float = 3.0, meta_cpa: float = 60.0) -> dict:
    """
    Calcula o Score de Saúde da Conta (0–100) com base em 4 KPIs ponderados.

    Pesos:
        ROAS        → 40% (principal indicador de retorno)
        CTR         → 20% (qualidade do anúncio/segmentação)
        Conv. Rate  → 20% (qualidade da oferta/landing page)
        CPA         → 20% (eficiência de custo — inverso)

    Grades: A+ (90-100) · A (80-89) · B+ (70-79) · B (60-69)
            C (50-59) · D (40-49) · F (<40)
    """
    roas  = metricas.get("roas",  0)
    ctr   = metricas.get("ctr",   0)
    conv  = metricas.get("taxa_conversao", 0)
    cpa   = metricas.get("cpa",   999)

    # ── Pontuação individual por KPI ─────────────────────────
    def score_roas(v):
        if v >= meta_roas * 2.0: return 100
        if v >= meta_roas * 1.3: return 85
        if v >= meta_roas:       return 70
        if v >= meta_roas * 0.7: return 50
        if v >= meta_roas * 0.4: return 30
        return 10

    def score_ctr(v):
        if v >= 4.0: return 100
        if v >= 3.0: return 80
        if v >= 2.0: return 60
        if v >= 1.0: return 40
        return 20

    def score_conv(v):
        if v >= 5.0: return 100
        if v >= 3.0: return 80
        if v >= 2.0: return 60
        if v >= 1.0: return 40
        return 20

    def score_cpa(v):   # inverso — CPA menor = melhor, relativo à meta
        if v <= meta_cpa * 0.35: return 100
        if v <= meta_cpa * 0.65: return 80
        if v <= meta_cpa:        return 60
        if v <= meta_cpa * 2.0:  return 40
        return 20

    breakdown = {
        "ROAS":            (score_roas(roas),  0.40),
        "CTR":             (score_ctr(ctr),    0.20),
        "Conv. Rate":      (score_conv(conv),  0.20),
        "CPA (eficiência)":(score_cpa(cpa),    0.20),
    }

    total = round(sum(s * w for s, w in breakdown.values()))

    # ── Grade e cor ───────────────────────────────────────────
    if total >= 90: grade, cor, label = "A+", "#10B981", "Excelente"
    elif total >= 80: grade, cor, label = "A",  "#34D399", "Muito Bom"
    elif total >= 70: grade, cor, label = "B+", "#6EE7B7", "Bom"
    elif total >= 60: grade, cor, label = "B",  "#FCD34D", "Acima da Média"
    elif total >= 50: grade, cor, label = "C",  "#FBBF24", "Na Média"
    elif total >= 40: grade, cor, label = "D",  "#F97316", "Abaixo da Média"
    else:             grade, cor, label = "F",  "#EF4444", "Crítico"

    return {
        "score": total, "grade": grade,
        "cor": cor, "label": label,
        "breakdown": breakdown,
    }


def render_health_score(score_data: dict) -> None:
    """
    Exibe o Score de Saúde como gauge Plotly + breakdown dos componentes.
    """
    score = score_data["score"]
    cor   = score_data["cor"]
    grade = score_data["grade"]
    label = score_data["label"]

    # ── Gauge Plotly ──────────────────────────────────────────
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(suffix="", font=dict(size=38, color="#F1F5F9")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#475569",
                      tickfont=dict(color="#475569", size=10)),
            bar=dict(color=cor, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0,  40], color="rgba(239,68,68,0.08)"),
                dict(range=[40, 70], color="rgba(245,158,11,0.08)"),
                dict(range=[70,100], color="rgba(16,185,129,0.08)"),
            ],
            threshold=dict(line=dict(color=cor, width=3), value=score),
        ),
        domain=dict(x=[0,1], y=[0,1]),
    ))

    fig.update_layout(
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=0),
        annotations=[dict(
            text=f"<b>{grade}</b> — {label}",
            x=0.5, y=0.18, showarrow=False,
            font=dict(size=13, color=cor),
        )],
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Breakdown por KPI ─────────────────────────────────────
    st.markdown("<div style='margin-top:-10px'>", unsafe_allow_html=True)
    for kpi, (pts, peso) in score_data["breakdown"].items():
        pct  = int(pts * peso)
        fill = "#10B981" if pts >= 70 else "#F59E0B" if pts >= 50 else "#EF4444"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;font-size:0.75rem;">
            <span style="color:#9CA3AF;width:120px;flex-shrink:0;">{kpi}</span>
            <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:6px;">
                <div style="width:{pts}%;background:{fill};height:6px;border-radius:4px;"></div>
            </div>
            <span style="color:{fill};font-weight:700;width:32px;text-align:right;">{pct}pt</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================
# 🕐 MÓDULO 10 — HISTÓRICO DE DIAGNÓSTICOS
# =============================================================

def salvar_historico(diagnostico_txt: str, metricas: dict,
                     periodo_label: str) -> None:
    """
    Salva o diagnóstico atual no histórico da sessão (máx. 5 entradas).
    Cada entrada contém timestamp, métricas resumidas e texto completo.
    """
    if "historico_diagnosticos" not in st.session_state:
        st.session_state.historico_diagnosticos = []

    entrada = {
        "timestamp":  datetime.now().strftime("%d/%m/%Y %H:%M"),
        "periodo":    periodo_label,
        "roas":       metricas.get("roas", 0),
        "cpa":        metricas.get("cpa",  0),
        "receita":    metricas.get("receita_total", 0),
        "texto":      diagnostico_txt,
    }

    # Evita duplicata imediata (mesmo texto)
    if st.session_state.historico_diagnosticos:
        if st.session_state.historico_diagnosticos[-1]["texto"] == diagnostico_txt:
            return

    st.session_state.historico_diagnosticos.append(entrada)
    # Mantém apenas os 5 mais recentes
    st.session_state.historico_diagnosticos = (
        st.session_state.historico_diagnosticos[-5:]
    )


def render_historico_diagnosticos() -> None:
    """
    Exibe os últimos 5 diagnósticos gerados na sessão em cards expansíveis.
    Mostra resumo (ROAS, CPA, Receita) e permite re-visualizar o texto completo.
    """
    historico = st.session_state.get("historico_diagnosticos", [])
    if not historico:
        return

    st.markdown('<div class="sec-title">🕐 Histórico de Diagnósticos</div>',
                unsafe_allow_html=True)

    # Exibe do mais recente para o mais antigo
    for i, entrada in enumerate(reversed(historico)):
        label = "Mais recente" if i == 0 else f"Diagnóstico anterior #{i}"
        with st.expander(
            f"📋 {label} — {entrada['timestamp']} · {entrada['periodo']}",
            expanded=(i == 0),
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("ROAS",    f"{entrada['roas']:.2f}×")
            c2.metric("CPA",     f"R$ {entrada['cpa']:,.2f}")
            c3.metric("Receita", f"R$ {entrada['receita']:,.0f}")
            st.markdown("---")
            st.markdown(entrada["texto"])



@st.dialog("🚀 Bem-vindo ao AdPerform AI", width="large")
def mostrar_onboarding() -> None:
    """
    Modal de boas-vindas exibido no primeiro acesso.
    Explica o produto em 3 passos e orienta a primeira ação.
    Dispensado ao clicar em "Começar" — nunca mais aparece na sessão.
    """
    st.markdown("""
    <div style="text-align:center;padding:8px 0 20px;">
        <div style="font-size:2.5rem;">🚀</div>
        <div style="font-size:1.1rem;font-weight:700;color:#F1F5F9;margin-top:8px;">
            Dashboard de Performance com Diagnóstico por IA
        </div>
        <div style="font-size:0.85rem;color:#64748B;margin-top:6px;">
            Para Gestores de Tráfego Pago e Agências de Marketing
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, titulo, desc in [
        (c1, "📁", "1. Conecte seus dados",
         "Faça upload de um **CSV ou Excel** exportado do Google Ads / Meta Ads, "
         "ou conecte uma planilha Google Sheets pelo link CSV público."),
        (c2, "📊", "2. Analise os KPIs",
         "Veja **ROAS, CPA, CPC, CTR** e Taxa de Conversão em tempo real, "
         "com comparativo do período anterior e alertas automáticos."),
        (c3, "🤖", "3. Gere o diagnóstico",
         "A IA atua como **Diretor de Growth** e entrega diagnóstico, "
         "onde o dinheiro está bem gasto e plano de ação para a semana."),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:rgba(37,99,235,0.08);border:1px solid rgba(37,99,235,0.18);
                        border-radius:12px;padding:16px;text-align:center;height:100%;">
                <div style="font-size:2rem;">{icon}</div>
                <div style="font-size:0.82rem;font-weight:700;color:#93C5FD;margin:8px 0 6px;">{titulo}</div>
                <div style="font-size:0.75rem;color:#64748B;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📋 Estrutura obrigatória do arquivo (nomes exatos nas colunas):**")
    st.code("data | campanha | canal | investimento | impressoes | cliques | conversoes | receita",
            language=None)

    col_dl, col_btn = st.columns([1, 1])
    with col_dl:
        try:
            template = gerar_template_excel()
            st.download_button(
                "⬇️ Baixar template Excel",
                data=template,
                file_name="template_adperform_ai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception:
            st.caption("Template disponível na sidebar")
    with col_btn:
        if st.button("Entendido — Vamos começar! 🚀", type="primary", use_container_width=True):
            st.session_state.onboarding_visto = True
            st.rerun()


def main() -> None:
    # ── 0. Onboarding (primeiro acesso) ────────────────────────
    if "onboarding_visto" not in st.session_state:
        st.session_state.onboarding_visto = False
    if not st.session_state.onboarding_visto:
        mostrar_onboarding()

    # ── 1. Sidebar ─────────────────────────────────────────────
    url_planilha, arquivo_upload, api_key, groq_key, meta_roas, meta_cpa = render_sidebar()

    # ── 2. Carregamento de dados (Prioridade: Upload > Sheets > Simulados) ──
    df: Optional[pd.DataFrame] = None
    fonte = "📊 Dados Simulados"

    if arquivo_upload is not None:
        with st.spinner(f"⏳ Processando {arquivo_upload.name}..."):
            df = carregar_dados_upload(arquivo_upload)
        if df is not None and not df.empty:
            fonte = f"📁 {arquivo_upload.name}"
            st.toast(f"✅ {len(df)} registros carregados", icon="📂")
        else:
            st.warning("Arquivo inválido. Usando dados simulados.")

    elif url_planilha:
        with st.spinner("⏳ Conectando ao Google Sheets..."):
            df = carregar_dados_planilha(url_planilha)
        if df is not None and not df.empty:
            fonte = "🔗 Google Sheets"
            st.toast("✅ Planilha conectada!", icon="📋")
        else:
            st.warning("Não foi possível carregar. Usando dados simulados.")

    if df is None or df.empty:
        df = gerar_dados_simulados()
        df["data"] = pd.to_datetime(df["data"])

    data_ini = df["data"].min().strftime("%d/%m/%Y")
    data_fim = df["data"].max().strftime("%d/%m/%Y")

    # ── 3. Header ──────────────────────────────────────────────
    render_header(fonte, data_ini, data_fim, api_key)

    st.markdown(f"""
    <div class="source-tag">
        {fonte} &nbsp;·&nbsp; {data_ini} → {data_fim} &nbsp;·&nbsp; {len(df):,} registros
    </div>
    """, unsafe_allow_html=True)

    # ── 4. Filtros ──────────────────────────────────────────────
    periodo_dias, canais_sel, campanhas_sel = render_filtros(df)

    # Aplica filtros no período atual
    df_atual = aplicar_filtros(df, periodo_dias, canais_sel, campanhas_sel)
    if df_atual.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros.")
        st.stop()

    # Hash dos filtros atuais — detecta se o diagnóstico ficou desatualizado
    filtros_hash = hash((periodo_dias, tuple(sorted(canais_sel)), tuple(sorted(campanhas_sel))))
    if "filtros_hash" not in st.session_state:
        st.session_state.filtros_hash = filtros_hash
    diagnostico_desatualizado = (
        st.session_state.diagnostico_txt is not None
        and st.session_state.filtros_hash != filtros_hash
    )

    # ── 5. Métricas + Comparativo ───────────────────────────────
    metricas         = calcular_metricas(df_atual)
    metricas_ant     = calcular_periodo_anterior(df, periodo_dias, canais_sel, campanhas_sel)
    deltas           = calcular_deltas(metricas, metricas_ant)
    periodo_label    = f"Últimos {periodo_dias} dias"

    # ── 6. Alertas Automáticos ──────────────────────────────────
    render_alertas(metricas, meta_roas=meta_roas, meta_cpa=meta_cpa)

    # ── 7. KPI Cards com comparativo ───────────────────────────
    cmp_txt = f" vs {periodo_dias} dias anteriores" if metricas_ant else ""
    st.markdown(f'<div class="sec-title">📊 KPIs — {periodo_label}{cmp_txt}</div>', unsafe_allow_html=True)
    render_kpis_cards(metricas, deltas, df_completo=df, periodo_dias=periodo_dias)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 8. Resumo Financeiro ────────────────────────────────────
    st.markdown('<div class="sec-title">💰 Resumo Financeiro</div>', unsafe_allow_html=True)
    render_resumo_financeiro(metricas)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<hr style="border-color:rgba(59,130,246,0.1);margin:4px 0 20px;">', unsafe_allow_html=True)

    # ── 9. Health Score ─────────────────────────────────────────
    score_data = calcular_health_score(metricas, meta_roas=meta_roas, meta_cpa=meta_cpa)
    st.markdown('<div class="sec-title">🏆 Score de Saúde da Conta</div>', unsafe_allow_html=True)
    col_score, col_grafprinc = st.columns([1, 3], gap="medium")
    with col_score:
        render_health_score(score_data)
    with col_grafprinc:
        st.plotly_chart(grafico_investimento_receita(df_atual), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 10. Gráficos de análise ──────────────────────────────────
    st.markdown('<div class="sec-title">📈 Análise Visual</div>', unsafe_allow_html=True)
    col_g1, col_g2, col_g3 = st.columns([2, 2, 2], gap="medium")
    with col_g1:
        st.plotly_chart(grafico_roas_campanhas(metricas, meta_roas=meta_roas), use_container_width=True)
    with col_g2:
        donut_por = st.radio("Distribuição por:", ["canal", "campanha"],
                             horizontal=True, label_visibility="collapsed")
        st.plotly_chart(grafico_distribuicao_investimento(df_atual, por=donut_por),
                        use_container_width=True)
    with col_g3:
        st.plotly_chart(grafico_eficiencia_temporal(df_atual), use_container_width=True)

    # ── 11. Tabela detalhada ────────────────────────────────────
    with st.expander("📋 Detalhamento por Campanha", expanded=False):
        render_tabela_campanhas(metricas)

    st.markdown('<hr style="border-color:rgba(59,130,246,0.1);margin:20px 0;">', unsafe_allow_html=True)

    # ── 12. Diagnóstico IA ──────────────────────────────────────
    st.markdown('<div class="sec-title">🤖 Diagnóstico por IA</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
        <span style="font-size:0.82rem;color:#64748B;">
            Análise executiva gerada pelo Gemini 2.0 Flash &nbsp;·&nbsp;
            Atuando como Diretor de Growth
        </span>
        <span style="background:rgba(37,99,235,0.12);border:1px solid rgba(37,99,235,0.25);
                     border-radius:12px;padding:2px 8px;font-size:0.63rem;
                     font-weight:700;color:#93C5FD;letter-spacing:0.05em;">AI POWERED</span>
    </div>
    """, unsafe_allow_html=True)

    if "diagnostico_txt" not in st.session_state:
        st.session_state.diagnostico_txt = None

    tem_alguma_key = bool(api_key or groq_key)
    if not tem_alguma_key:
        st.markdown("""
        <div style="background:rgba(37,99,235,0.07);border:1px solid rgba(37,99,235,0.18);
                    border-radius:10px;padding:14px 18px;font-size:0.83rem;color:#93C5FD;">
            🔑 Configure uma API Key na sidebar para ativar o diagnóstico.<br>
            <span style="color:#475569;font-size:0.75rem;">
                <strong>Gemini:</strong> aistudio.google.com &nbsp;·&nbsp;
                <strong>Groq (grátis):</strong> console.groq.com
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        if diagnostico_desatualizado:
            st.markdown("""
            <div style="background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.30);
                        border-radius:10px;padding:11px 16px;margin-bottom:12px;
                        font-size:0.82rem;color:#FCD34D;display:flex;gap:10px;align-items:center;">
                <span>⚠️</span>
                <span><strong>Diagnóstico desatualizado</strong> — os filtros mudaram desde a última análise.
                Clique em <strong>Gerar Diagnóstico</strong> para atualizar com os dados atuais.</span>
            </div>
            """, unsafe_allow_html=True)

        col_btn, _ = st.columns([1, 3])
        gerar_btn = col_btn.button("⚡ Gerar Diagnóstico", type="primary", use_container_width=True)

        if gerar_btn:
            provider = "Gemini" if api_key else "Groq"
            with st.spinner(f"🧠 {provider} analisando campanhas… pode levar alguns segundos"):
                st.session_state.diagnostico_txt = gerar_diagnostico_ia(metricas, api_key, groq_key)
            # Atualiza o hash salvo e o histórico
            if st.session_state.diagnostico_txt:
                st.session_state.filtros_hash = filtros_hash
                salvar_historico(st.session_state.diagnostico_txt, metricas, periodo_label)

        if st.session_state.diagnostico_txt:
            with st.chat_message("assistant", avatar="🤖"):
                if diagnostico_desatualizado and not gerar_btn:
                    st.caption("⚠️ Análise do período anterior — atualize clicando em Gerar Diagnóstico")
                st.markdown(st.session_state.diagnostico_txt)

            col_dl1, col_dl2, _ = st.columns([1, 1, 2])
            col_dl1.download_button(
                label="⬇️ Exportar (.txt)",
                data=st.session_state.diagnostico_txt,
                file_name=f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            try:
                pdf_bytes = gerar_pdf(
                    metricas,
                    st.session_state.diagnostico_txt,
                    periodo_label,
                    fonte,
                )
                col_dl2.download_button(
                    label="📄 Exportar PDF",
                    data=pdf_bytes,
                    file_name=f"relatorio_adperform_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as pdf_err:
                col_dl2.caption(f"PDF indisponível: {pdf_err}")

    # ── 13. Histórico de Diagnósticos ──────────────────────────
    render_historico_diagnosticos()

    # ── 14. Rodapé ──────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(59,130,246,0.1);padding-top:16px;margin-top:20px;
                display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <span style="font-size:0.72rem;color:#334155;font-weight:600;">
            🚀 AdPerform AI · Dashboard de Performance
        </span>
        <span style="font-size:0.68rem;color:#1E293B;">
            Streamlit · Pandas · Plotly · Gemini AI
        </span>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# ENTRY POINT
# =============================================================
if __name__ == "__main__":
    main()