# ============================================================
# 🚀 AdPerform AI — Dashboard de Performance com Diagnóstico por IA
#
# Nicho   : Gestores de Tráfego Pago e Agências de Marketing
# Stack   : Streamlit + Pandas + Plotly + Gemini AI
# Deploy  : Streamlit Community Cloud (gratuito)
# Execução: streamlit run app.py
# ============================================================

from __future__ import annotations

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

# CSS mínimo para polir métricas e espaçamentos
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 1.55rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.82rem; color: #6b7280; }
    .block-container { padding-top: 1.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# 📊 MÓDULO 1 — DADOS
#     Dados simulados (demo) e carregamento via Google Sheets
# =============================================================

def gerar_dados_simulados() -> pd.DataFrame:
    """
    Cria um DataFrame com 30 dias de dados realistas de campanhas de tráfego pago.
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

    for i in range(30):
        data = hoje - timedelta(days=29 - i)
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


def gerar_diagnostico_ia(metricas: dict, api_key: str) -> str:
    """
    Chama a API do Gemini com os dados de performance e retorna
    um diagnóstico executivo em Markdown.

    Args:
        metricas (dict): KPIs calculados por calcular_metricas()
        api_key  (str):  Chave da API do Google AI Studio

    Returns:
        str: Relatório em Markdown ou mensagem de erro
    """
    import google.generativeai as genai  # import lazy para evitar erro sem lib

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",          # rápido e eficiente para análise
        system_instruction=_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=0.35,          # mais focado; menos "criativo" para análise
            max_output_tokens=1024,
        ),
    )

    # Serializa tabela de campanhas para o prompt
    df_camp = (
        metricas["por_campanha"][[
            "campanha", "canal", "investimento", "receita",
            "conversoes", "cliques", "roas", "cpa", "ctr",
        ]]
        .sort_values("roas", ascending=False)
    )
    tabela_str = df_camp.to_string(index=False, float_format="{:.2f}".format)

    prompt_usuario = f"""
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

    try:
        response = model.generate_content(prompt_usuario)
        return response.text
    except Exception as exc:
        msg = str(exc).lower()
        if "api_key" in msg or "invalid" in msg or "permission" in msg:
            return "❌ **API Key inválida ou sem permissão.** Verifique a chave no Google AI Studio."
        if "quota" in msg or "limit" in msg:
            return "⚠️ **Cota da API atingida.** Aguarde alguns minutos e tente novamente."
        return f"❌ **Erro inesperado na API do Gemini:**\n```\n{exc}\n```"


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


def grafico_roas_campanhas(metricas: dict) -> go.Figure:
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
# 🖥️  MÓDULO 5 — INTERFACE STREAMLIT
#     Sidebar, KPIs, gráficos e diagnóstico de IA
# =============================================================

def render_sidebar() -> tuple[str, str]:
    """
    Renderiza o painel lateral e retorna (url_planilha, api_key).

    A API key é lida — em ordem de prioridade — de:
      1. st.secrets["GEMINI_API_KEY"]  ← Streamlit Cloud / secrets.toml local
      2. Campo de texto na sidebar     ← modo desenvolvimento local
    """
    with st.sidebar:
        st.markdown("## 🚀 AdPerform AI")
        st.caption("Dashboard de Performance com Diagnóstico por IA")
        st.divider()

        # ── Fonte de Dados ──────────────────────────────────────
        st.markdown("### 📋 Fonte de Dados")
        usar_sheets = st.toggle("Conectar Google Sheets", value=False)
        url_planilha = ""

        if usar_sheets:
            url_planilha = st.text_input(
                "URL CSV da planilha",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                help=(
                    "Como obter a URL:\n"
                    "Arquivo → Publicar na Web → "
                    "Selecione a aba → Formato CSV → Publicar → Copie o link"
                ),
            )
            if url_planilha and "format=csv" not in url_planilha:
                st.caption("💡 Certifique-se de que a URL termina com `format=csv`")

        st.divider()

        # ── API Key Gemini ──────────────────────────────────────
        st.markdown("### 🤖 Gemini AI")
        api_key = ""

        try:
            # Tenta carregar dos Secrets (produção no Streamlit Cloud)
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ API Key carregada dos Secrets", icon="🔐")
        except (KeyError, FileNotFoundError):
            # Fallback: input manual para desenvolvimento local
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIzaSy...",
                help=(
                    "Obtenha gratuitamente em:\n"
                    "https://aistudio.google.com/app/apikey"
                ),
            )
            if not api_key:
                st.info("Configure a API Key para ativar o diagnóstico.", icon="🔑")

        st.divider()

        # ── Rodapé da sidebar ───────────────────────────────────
        st.caption("v1.0.0 — MVP de Performance AI")
        st.caption("Powered by Gemini 2.0 Flash + Streamlit")

    return url_planilha, api_key


def render_kpis(metricas: dict) -> None:
    """Renderiza 5 cards de KPIs no topo do dashboard."""
    roas       = metricas["roas"]
    meta_ok    = roas >= 3.0
    delta_roas = f"✅ Acima da meta (3×)" if meta_ok else "⚠️ Abaixo da meta (3×)"
    cor_delta  = "normal" if meta_ok else "inverse"

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        label="💰 ROAS",
        value=f"{roas:.2f}×",
        delta=delta_roas,
        delta_color=cor_delta,
        help="Return on Ad Spend = Receita / Investimento",
    )
    c2.metric(
        label="🎯 CPA",
        value=f"R$ {metricas['cpa']:,.2f}",
        help="Custo por Aquisição = Investimento / Conversões",
    )
    c3.metric(
        label="🖱️ CPC",
        value=f"R$ {metricas['cpc']:,.2f}",
        help="Custo por Clique = Investimento / Cliques",
    )
    c4.metric(
        label="👁️ CTR",
        value=f"{metricas['ctr']:.2f}%",
        help="Click-Through Rate = Cliques / Impressões",
    )
    c5.metric(
        label="✅ Taxa de Conversão",
        value=f"{metricas['taxa_conversao']:.2f}%",
        help="Taxa de Conversão = Conversões / Cliques",
    )


def render_resumo_financeiro(metricas: dict) -> None:
    """Renderiza 3 cards com o resumo financeiro do período."""
    c1, c2, c3 = st.columns(3)
    lucro = metricas["lucro_liquido"]

    c1.metric("💸 Investimento Total", f"R$ {metricas['investimento_total']:,.2f}")
    c2.metric("💵 Receita Gerada",     f"R$ {metricas['receita_total']:,.2f}")
    c3.metric(
        "📈 Lucro Líquido",
        f"R$ {lucro:,.2f}",
        delta="Positivo" if lucro > 0 else "Negativo",
        delta_color="normal" if lucro > 0 else "inverse",
    )


def render_tabela_campanhas(metricas: dict) -> None:
    """
    Tabela formatada com heatmap de ROAS e CPA por campanha.
    Cores: verde = bom, vermelho = ruim.
    """
    df_exib = metricas["por_campanha"].copy()
    df_exib = df_exib.sort_values("roas", ascending=False)
    df_exib.columns = [
        "Campanha", "Canal", "Invest. (R$)", "Receita (R$)",
        "Conversões", "Cliques", "Impressões", "ROAS", "CPA (R$)", "CTR (%)",
    ]

    st.dataframe(
        df_exib.style
            .format({
                "Invest. (R$)": "R$ {:,.2f}",
                "Receita (R$)": "R$ {:,.2f}",
                "CPA (R$)":     "R$ {:,.2f}",
                "ROAS":         "{:.2f}×",
                "CTR (%)":      "{:.2f}%",
            })
            .background_gradient(subset=["ROAS"],    cmap="RdYlGn", vmin=1.0, vmax=5.5)
            .background_gradient(subset=["CPA (R$)"], cmap="RdYlGn_r"),
        use_container_width=True,
        hide_index=True,
        height=230,
    )


# =============================================================
# 🎬 MAIN — Orquestra o app completo
# =============================================================

def main() -> None:
    # ── 1. Sidebar ─────────────────────────────────────────────
    url_planilha, api_key = render_sidebar()

    # ── 2. Cabeçalho ───────────────────────────────────────────
    st.markdown("# 🚀 AdPerform AI")
    st.markdown(
        "**Dashboard de Performance de Vendas com Diagnóstico Automatizado por IA**  \n"
        "*Para Gestores de Tráfego Pago e Agências de Marketing*"
    )
    st.divider()

    # ── 3. Carregamento de dados ────────────────────────────────
    df: Optional[pd.DataFrame] = None
    fonte = "📊 Dados Simulados (demo)"

    if url_planilha:
        with st.spinner("⏳ Carregando dados do Google Sheets..."):
            df = carregar_dados_planilha(url_planilha)

        if df is not None and not df.empty:
            fonte = "🔗 Google Sheets (live)"
            st.toast("✅ Planilha carregada com sucesso!", icon="📋")
        else:
            st.warning("Não foi possível carregar a planilha. Usando dados simulados.")

    if df is None or df.empty:
        df = gerar_dados_simulados()
        df["data"] = pd.to_datetime(df["data"])

    # Caption com metadados da fonte
    data_ini = df["data"].min().strftime("%d/%m/%Y")
    data_fim = df["data"].max().strftime("%d/%m/%Y")
    st.caption(
        f"Fonte: **{fonte}** &nbsp;|&nbsp; "
        f"Período: {data_ini} → {data_fim} &nbsp;|&nbsp; "
        f"{len(df):,} registros carregados"
    )

    # ── 4. Cálculo de métricas ──────────────────────────────────
    metricas = calcular_metricas(df)

    # ── 5. KPIs principais ──────────────────────────────────────
    st.subheader("📊 KPIs do Período")
    render_kpis(metricas)

    st.markdown("<br>", unsafe_allow_html=True)
    render_resumo_financeiro(metricas)

    st.divider()

    # ── 6. Gráficos ─────────────────────────────────────────────
    col_g1, col_g2 = st.columns([3, 2], gap="medium")
    with col_g1:
        st.plotly_chart(grafico_investimento_receita(df), use_container_width=True)
    with col_g2:
        st.plotly_chart(grafico_roas_campanhas(metricas), use_container_width=True)

    # ── 7. Tabela detalhada (colapsável) ────────────────────────
    with st.expander("📋 Detalhamento por Campanha", expanded=False):
        render_tabela_campanhas(metricas)

    st.divider()

    # ── 8. Diagnóstico por IA ───────────────────────────────────
    st.subheader("🤖 Diagnóstico Executivo por IA")
    st.caption("Análise gerada pelo Gemini 2.0 Flash atuando como Diretor de Growth")

    # Persiste o diagnóstico no session_state para sobreviver a reruns do Streamlit
    if "diagnostico_txt" not in st.session_state:
        st.session_state.diagnostico_txt = None

    if not api_key:
        st.info(
            "Configure sua **Gemini API Key** na sidebar para ativar o diagnóstico.  \n"
            "Obtenha gratuitamente em [aistudio.google.com](https://aistudio.google.com/app/apikey).",
            icon="🔑",
        )
    else:
        col_btn, _ = st.columns([1, 3])
        gerar_btn = col_btn.button(
            "⚡ Gerar Diagnóstico", type="primary", use_container_width=True
        )

        if gerar_btn:
            with st.spinner("🧠 Gemini analisando suas campanhas… isso leva alguns segundos"):
                st.session_state.diagnostico_txt = gerar_diagnostico_ia(metricas, api_key)

        if st.session_state.diagnostico_txt:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(st.session_state.diagnostico_txt)

            # Botão para exportar o relatório como .txt
            st.download_button(
                label="⬇️ Exportar Relatório (.txt)",
                data=st.session_state.diagnostico_txt,
                file_name=f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
            )

    # ── 9. Rodapé ───────────────────────────────────────────────
    st.divider()
    st.caption(
        "🚀 **AdPerform AI** | Dashboard de Performance &nbsp;·&nbsp; "
        "Desenvolvido com Streamlit · Pandas · Plotly · Gemini AI"
    )


# =============================================================
# ENTRY POINT
# =============================================================
if __name__ == "__main__":
    main()