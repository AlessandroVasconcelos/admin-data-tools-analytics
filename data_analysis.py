import streamlit as st
import pandas as pd
import altair as alt


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _colunas_numericas(df: pd.DataFrame):
    """Retorna lista de colunas numéricas e o dataframe já convertido."""
    df_num = df.copy()
    for col in df_num.columns:
        df_num[col] = pd.to_numeric(df_num[col], errors="coerce")
    colunas = [c for c in df_num.columns if df_num[c].notna().sum() > 0]
    return colunas, df_num


def _colunas_texto(df: pd.DataFrame, colunas_num: list) -> list:
    return [c for c in df.columns if c not in colunas_num]


def _pizza_altair(df_pizza: pd.DataFrame, col_label: str, col_valor: str, titulo: str = ""):
    """Gera um gráfico de pizza sem dependência de matplotlib."""
    chart = (
        alt.Chart(df_pizza, title=titulo)
        .mark_arc(outerRadius=110, innerRadius=40)
        .encode(
            theta=alt.Theta(field=col_valor, type="quantitative"),
            color=alt.Color(
                field=col_label,
                type="nominal",
                legend=alt.Legend(orient="right", labelLimit=200),
            ),
            tooltip=[col_label, col_valor],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


# ─────────────────────────────────────────────
# SEÇÕES
# ─────────────────────────────────────────────

def _secao_preview(df: pd.DataFrame):
    st.markdown("### 👁️ Pré-visualização dos Dados")
    st.dataframe(df, use_container_width=True, height=220)
    st.markdown("---")


def _secao_resumo_geral(df: pd.DataFrame, colunas_num: list, colunas_txt: list):
    st.markdown("### 🗂️ Resumo Geral da Planilha")

    total_linhas  = len(df)
    total_colunas = len(df.columns)
    total_celulas = total_linhas * total_colunas
    total_vazios  = int(df.replace("", pd.NA).isna().sum().sum())
    preenchidos   = total_celulas - total_vazios
    pct_completo  = (preenchidos / total_celulas * 100) if total_celulas > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Linhas",            total_linhas)
    c2.metric("📊 Colunas",           total_colunas)
    c3.metric("🔢 Colunas Numéricas", len(colunas_num))
    c4.metric("🔤 Colunas de Texto",  len(colunas_txt))

    st.metric(
        "✅ Completude da Planilha",
        f"{pct_completo:.1f}%",
        help=f"{preenchidos} células preenchidas de {total_celulas} no total."
    )

    # Pizza: preenchido vs vazio
    if total_vazios > 0:
        df_pizza_comp = pd.DataFrame({
            "Status":     ["Preenchido", "Vazio"],
            "Quantidade": [preenchidos, total_vazios],
        })
        _pizza_altair(df_pizza_comp, "Status", "Quantidade", "Completude Geral")

    # Pizza: numéricas vs texto
    df_pizza_tipo = pd.DataFrame({
        "Tipo":       ["Numérico", "Texto"],
        "Quantidade": [len(colunas_num), len(colunas_txt)],
    })
    _pizza_altair(df_pizza_tipo, "Tipo", "Quantidade", "Tipos de Colunas")

    st.markdown("---")


def _secao_qualidade(df: pd.DataFrame):
    st.markdown("### 🔍 Qualidade dos Dados por Coluna")

    df_tmp = df.replace("", pd.NA)
    resumo = pd.DataFrame({
        "Coluna":        df.columns,
        "Preenchidos":   [df_tmp[c].notna().sum() for c in df.columns],
        "Vazios":        [df_tmp[c].isna().sum()  for c in df.columns],
        "% Preenchido":  [
            f"{df_tmp[c].notna().sum() / len(df) * 100:.1f}%" if len(df) > 0 else "0%"
            for c in df.columns
        ],
        "Únicos":        [df_tmp[c].nunique() for c in df.columns],
        "Tipo Inferido": [
            "Numérico" if pd.to_numeric(df[c], errors="coerce").notna().sum() > len(df) * 0.5
            else "Texto"
            for c in df.columns
        ],
    })
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    # Pizza: vazios por coluna (só se houver algum)
    resumo_num = resumo.copy()
    resumo_num["Vazios_int"] = [df_tmp[c].isna().sum() for c in df.columns]
    cols_com_vazios = resumo_num[resumo_num["Vazios_int"] > 0]

    if not cols_com_vazios.empty:
        st.caption("🔴 Distribuição de valores vazios por coluna:")
        df_pizza_vazios = pd.DataFrame({
            "Coluna": cols_com_vazios["Coluna"].tolist(),
            "Vazios": cols_com_vazios["Vazios_int"].tolist(),
        })
        _pizza_altair(df_pizza_vazios, "Coluna", "Vazios", "Vazios por Coluna")

    st.markdown("---")


def _secao_estatisticas(df: pd.DataFrame, df_num: pd.DataFrame, colunas_num: list):
    st.markdown("### 📐 Estatísticas Descritivas")

    if not colunas_num:
        st.info("Nenhuma coluna numérica detectada nesta planilha.")
        st.markdown("---")
        return

    coluna_stat = st.selectbox("Selecione a coluna numérica para analisar:", colunas_num, key="sel_stat")
    serie = df_num[coluna_stat].dropna()

    if len(serie) == 0:
        st.warning("A coluna selecionada não possui valores numéricos válidos.")
        st.markdown("---")
        return

    media      = serie.mean()
    mediana    = serie.median()
    moda_vals  = serie.mode()
    moda       = moda_vals.iloc[0] if not moda_vals.empty else None
    desvio     = serie.std()
    variancia  = serie.var()
    minimo     = serie.min()
    maximo     = serie.max()
    amplitude  = maximo - minimo
    q1         = serie.quantile(0.25)
    q3         = serie.quantile(0.75)
    iqr        = q3 - q1
    assimetria = serie.skew()
    curtose    = serie.kurt()
    cv         = (desvio / media * 100) if media != 0 else None

    st.markdown("#### Tendência Central")
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Média",   f"{media:.2f}")
    c2.metric("📍 Mediana", f"{mediana:.2f}")
    c3.metric("🔁 Moda",    f"{moda:.2f}" if moda is not None else "—")

    st.markdown("#### Dispersão")
    c4, c5, c6 = st.columns(3)
    c4.metric("📏 Desvio Padrão",  f"{desvio:.2f}")
    c5.metric("📐 Variância",       f"{variancia:.2f}")
    c6.metric("📉 Coef. Variação",  f"{cv:.1f}%" if cv is not None else "—")

    st.markdown("#### Extremos e Amplitude")
    c7, c8, c9 = st.columns(3)
    c7.metric("⬇️ Mínimo",    f"{minimo:.2f}")
    c8.metric("⬆️ Máximo",    f"{maximo:.2f}")
    c9.metric("↔️ Amplitude", f"{amplitude:.2f}")

    st.markdown("#### Quartis")
    c10, c11, c12 = st.columns(3)
    c10.metric("Q1 (25%)", f"{q1:.2f}")
    c11.metric("Q2 (50%)", f"{mediana:.2f}")
    c12.metric("Q3 (75%)", f"{q3:.2f}")
    st.metric(
        "📦 Intervalo Interquartil (IQR)", f"{iqr:.2f}",
        help="IQR = Q3 − Q1. Mede a dispersão dos 50% centrais dos dados."
    )

    st.markdown("#### Forma da Distribuição")
    c13, c14 = st.columns(2)
    direcao_assim = (
        "positiva (cauda à direita)"       if assimetria > 0
        else "negativa (cauda à esquerda)" if assimetria < 0
        else "simétrica"
    )
    tipo_curtose = (
        "leptocúrtica (picos acentuados)" if curtose > 0
        else "platocúrtica (achatada)"     if curtose < 0
        else "mesocúrtica (normal)"
    )
    c13.metric("📈 Assimetria (Skewness)", f"{assimetria:.4f}", help=f"Distribuição {direcao_assim}.")
    c14.metric("📉 Curtose (Kurtosis)",    f"{curtose:.4f}",    help=f"Distribuição {tipo_curtose}.")

    st.markdown("#### 📊 Distribuição de Frequência")
    num_bins      = min(20, len(serie.unique()))
    serie_cortada = pd.cut(serie, bins=num_bins)
    contagem_bins = serie_cortada.value_counts().sort_index()
    contagem_bins.index = [f"{i.left:.1f} – {i.right:.1f}" for i in contagem_bins.index]
    st.bar_chart(contagem_bins)

    with st.expander("📋 Ver tabela completa de estatísticas"):
        resumo = pd.DataFrame({
            "Estatística": [
                "Contagem", "Média", "Mediana", "Moda", "Desvio Padrão",
                "Variância", "Coef. de Variação (%)", "Mínimo", "Máximo",
                "Amplitude", "Q1 (25%)", "Q3 (75%)", "IQR", "Assimetria", "Curtose"
            ],
            "Valor": [
                int(serie.count()), f"{media:.4f}", f"{mediana:.4f}",
                f"{moda:.4f}" if moda is not None else "—",
                f"{desvio:.4f}", f"{variancia:.4f}",
                f"{cv:.2f}%" if cv is not None else "—",
                f"{minimo:.4f}", f"{maximo:.4f}", f"{amplitude:.4f}",
                f"{q1:.4f}", f"{q3:.4f}", f"{iqr:.4f}",
                f"{assimetria:.4f}", f"{curtose:.4f}"
            ]
        })
        st.dataframe(resumo, use_container_width=True, hide_index=True)

    st.markdown("---")


def _secao_distribuicao_texto(df: pd.DataFrame, colunas_txt: list):
    st.markdown("### 🔤 Distribuição de Colunas de Texto")

    if not colunas_txt:
        st.info("Nenhuma coluna de texto detectada.")
        st.markdown("---")
        return

    coluna_txt = st.selectbox("Selecione a coluna de texto:", colunas_txt, key="sel_txt")
    dados = df[coluna_txt].replace("", pd.NA).dropna()

    if len(dados) == 0:
        st.warning("Coluna vazia.")
        st.markdown("---")
        return

    n_unicos = dados.nunique()
    st.caption(f"{n_unicos} valores únicos encontrados nesta coluna.")

    contagem = dados.value_counts().head(20)

    if n_unicos > 100:
        st.warning(
            f"Esta coluna tem {n_unicos} valores únicos — exibindo os 20 mais frequentes."
        )

    # Barra + Pizza lado a lado
    col_bar, col_pie = st.columns(2)

    with col_bar:
        st.caption("📊 Gráfico de Barras")
        st.bar_chart(contagem)

    with col_pie:
        st.caption("🥧 Gráfico de Pizza")
        df_pizza = pd.DataFrame({
            "Valor":      contagem.index.tolist(),
            "Frequência": contagem.values.tolist(),
        })
        _pizza_altair(df_pizza, "Valor", "Frequência")

    with st.expander("📋 Ver tabela de frequência completa"):
        tabela = dados.value_counts().reset_index()
        tabela.columns = [coluna_txt, "Frequência"]
        tabela["% do Total"] = (tabela["Frequência"] / len(dados) * 100).map(lambda x: f"{x:.1f}%")
        st.dataframe(tabela, use_container_width=True, hide_index=True)

    st.markdown("---")


def _secao_correlacao(df_num: pd.DataFrame, colunas_num: list):
    if len(colunas_num) < 2:
        return

    st.markdown("### 🔗 Correlação entre Colunas Numéricas")
    st.caption("Valores próximos de 1 ou -1 indicam forte relação entre as colunas.")

    corr = df_num[colunas_num].corr().round(2)

    def colorir_celula(val):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return ""
        if v > 0:
            intensidade = int(v * 180)
            return f"background-color: rgba(0, {80 + intensidade}, 0, 0.6); color: white;"
        elif v < 0:
            intensidade = int(abs(v) * 180)
            return f"background-color: rgba({80 + intensidade}, 0, 0, 0.6); color: white;"
        else:
            return "background-color: rgba(200, 200, 0, 0.4); color: black;"

    st.dataframe(corr.style.map(colorir_celula), use_container_width=True)
    st.markdown("---")


def _secao_email(df: pd.DataFrame):
    col_email = next(
        (c for c in df.columns if c in ("email", "e-mail", "mail", "e_mail")),
        None
    )
    if col_email is None:
        return

    dados_email = df[col_email].replace("", pd.NA).dropna()
    if len(dados_email) == 0:
        return

    st.markdown("### 📧 Provedores de E-mail mais usados")
    dominios = dados_email.astype(str).apply(
        lambda x: x.split("@")[-1].lower() if "@" in x else None
    ).dropna()

    if len(dominios) == 0:
        return

    top = dominios.value_counts().head(10)

    col_bar, col_pie = st.columns(2)
    with col_bar:
        st.caption("📊 Gráfico de Barras")
        st.bar_chart(top)
    with col_pie:
        st.caption("🥧 Gráfico de Pizza")
        df_pizza = pd.DataFrame({
            "Provedor":    top.index.tolist(),
            "Quantidade":  top.values.tolist(),
        })
        _pizza_altair(df_pizza, "Provedor", "Quantidade")

    st.markdown("---")


# ─────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────

def renderizar_analise():
    if st.session_state.df_atual is None:
        st.warning("⚠️ Nenhuma planilha carregada! Por favor, vá em 'Conversor de Arquivos' e faça o upload primeiro.")
        return

    df = st.session_state.df_atual.copy()

    colunas_num, df_num = _colunas_numericas(df)
    colunas_txt         = _colunas_texto(df, colunas_num)

    _secao_preview(df)
    _secao_resumo_geral(df, colunas_num, colunas_txt)
    _secao_qualidade(df)
    _secao_estatisticas(df, df_num, colunas_num)
    _secao_distribuicao_texto(df, colunas_txt)
    _secao_correlacao(df_num, colunas_num)
    _secao_tabela_dinamica(df, colunas_num, colunas_txt)
    _secao_formatacao_condicional(df, colunas_num)
    _secao_tendencia(df, colunas_num)
    _secao_email(df)


# ─────────────────────────────────────────────
# TABELA DINÂMICA
# ─────────────────────────────────────────────

def _secao_tabela_dinamica(df: pd.DataFrame, colunas_num: list, colunas_txt: list):
    st.markdown("### 🔄 Tabela Dinâmica")
    st.caption("Resuma grandes volumes de dados agrupando por categorias e escolhendo a métrica.")

    if not colunas_txt:
        st.info("É necessário ao menos uma coluna de texto para agrupar.")
        st.markdown("---")
        return
    if not colunas_num:
        st.info("É necessário ao menos uma coluna numérica para calcular.")
        st.markdown("---")
        return

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        grupo = st.selectbox("Agrupar por (linha):", colunas_txt, key="td_grupo")
    with col_b:
        metrica_col = st.selectbox("Coluna de valor:", colunas_num, key="td_metrica_col")
    with col_c:
        operacao = st.selectbox("Operação:", ["Soma", "Média", "Contagem", "Máximo", "Mínimo"], key="td_op")

    # Segundo agrupamento opcional
    usar_segundo = st.checkbox("Adicionar segundo agrupamento (coluna)", key="td_segundo")
    grupo2 = None
    if usar_segundo:
        opcoes_g2 = [c for c in colunas_txt if c != grupo]
        if opcoes_g2:
            grupo2 = st.selectbox("Agrupar por (coluna):", opcoes_g2, key="td_grupo2")

    # Converte coluna numérica
    df_tmp = df.copy()
    df_tmp[metrica_col] = pd.to_numeric(df_tmp[metrica_col], errors="coerce")

    op_map = {"Soma": "sum", "Média": "mean", "Contagem": "count", "Máximo": "max", "Mínimo": "min"}
    func = op_map[operacao]

    try:
        if grupo2:
            tabela = df_tmp.pivot_table(
                index=grupo, columns=grupo2, values=metrica_col, aggfunc=func
            ).round(2)
        else:
            tabela = df_tmp.groupby(grupo)[metrica_col].agg(func).round(2).reset_index()
            tabela.columns = [grupo, f"{operacao} de {metrica_col}"]

        st.dataframe(tabela, use_container_width=True)

    except Exception as e:
        st.error(f"Não foi possível gerar a tabela dinâmica: {e}")

    st.markdown("---")


# ─────────────────────────────────────────────
# FORMATAÇÃO CONDICIONAL
# ─────────────────────────────────────────────

def _secao_formatacao_condicional(df: pd.DataFrame, colunas_num: list):
    st.markdown("### 🌡️ Formatação Condicional")
    st.caption("Identifique visualmente valores abaixo ou acima de uma meta definida por você.")

    if not colunas_num:
        st.info("Nenhuma coluna numérica disponível.")
        st.markdown("---")
        return

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        coluna_fc = st.selectbox("Coluna:", colunas_num, key="fc_col")
    
    df_tmp = df.copy()
    df_tmp[coluna_fc] = pd.to_numeric(df_tmp[coluna_fc], errors="coerce")
    serie_fc = df_tmp[coluna_fc].dropna()

    with col_b:
        meta_min = st.number_input(
            "Meta mínima (🔴 abaixo):",
            value=float(serie_fc.quantile(0.25)),
            key="fc_min"
        )
    with col_c:
        meta_max = st.number_input(
            "Meta máxima (🟢 acima):",
            value=float(serie_fc.quantile(0.75)),
            key="fc_max"
        )

    def colorir_linha(row):
        val = row[coluna_fc]
        try:
            v = float(val)
            if v >= meta_max:
                cor = "background-color: rgba(0, 180, 0, 0.25);"
            elif v < meta_min:
                cor = "background-color: rgba(220, 0, 0, 0.25);"
            else:
                cor = "background-color: rgba(255, 200, 0, 0.20);"
        except (TypeError, ValueError):
            cor = ""
        return [cor if c == coluna_fc else "" for c in row.index]

    # Mostra só colunas relevantes para não poluir
    colunas_exibir = list(dict.fromkeys(
        [c for c in df.columns if c not in colunas_num] + [coluna_fc]
    ))[:8]  # limita a 8 colunas

    df_exibir = df_tmp[colunas_exibir].copy()

    st.dataframe(
        df_exibir.style.apply(colorir_linha, axis=1),
        use_container_width=True,
        height=300
    )

    # Resumo do semáforo
    total = len(serie_fc)
    acima  = int((serie_fc >= meta_max).sum())
    abaixo = int((serie_fc < meta_min).sum())
    meio   = total - acima - abaixo

    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Acima da meta",    f"{acima}  ({acima/total*100:.1f}%)"  if total else "0")
    c2.metric("🟡 Dentro da faixa",  f"{meio}   ({meio/total*100:.1f}%)"   if total else "0")
    c3.metric("🔴 Abaixo da meta",   f"{abaixo} ({abaixo/total*100:.1f}%)" if total else "0")

    st.markdown("---")


# ─────────────────────────────────────────────
# GRÁFICO DE TENDÊNCIA
# ─────────────────────────────────────────────

def _secao_tendencia(df: pd.DataFrame, colunas_num: list):
    st.markdown("### 📈 Gráfico de Tendência")
    st.caption("Visualize se uma métrica sobe ou cai ao longo de uma sequência ou período.")

    if not colunas_num:
        st.info("Nenhuma coluna numérica disponível.")
        st.markdown("---")
        return

    todas_colunas = list(df.columns)

    col_a, col_b = st.columns(2)
    with col_a:
        eixo_x = st.selectbox(
            "Eixo X (sequência / tempo / categoria):",
            todas_colunas,
            key="tend_x"
        )
    with col_b:
        eixo_y = st.selectbox(
            "Eixo Y (valor numérico):",
            colunas_num,
            key="tend_y"
        )

    agregacao = st.selectbox(
        "Se houver repetições no eixo X, agregar por:",
        ["Média", "Soma", "Máximo", "Mínimo", "Contagem"],
        key="tend_agr"
    )
    op_map = {"Média": "mean", "Soma": "sum", "Máximo": "max", "Mínimo": "min", "Contagem": "count"}

    if eixo_x == eixo_y:
        st.warning("⚠️ O Eixo X e o Eixo Y não podem ser a mesma coluna. Escolha colunas diferentes.")
        st.markdown("---")
        return

    # Quando as colunas são diferentes, seleciona as duas de forma segura
    df_tend = df[[eixo_x, eixo_y]].copy()
    df_tend[eixo_y] = pd.to_numeric(df_tend[eixo_y].squeeze(), errors="coerce")
    df_tend = df_tend.dropna(subset=[eixo_y])

    # Tenta converter eixo X para data (try/except porque errors="ignore" foi removido no pandas 2.x)
    try:
        convertido = pd.to_datetime(df_tend[eixo_x], errors="coerce")
        if convertido.notna().sum() > len(df_tend) * 0.5:
            df_tend[eixo_x] = convertido
    except Exception:
        pass

    df_agr = (
        df_tend.groupby(eixo_x)[eixo_y]
        .agg(op_map[agregacao])
        .reset_index()
        .sort_values(eixo_x)
    )
    df_agr.columns = [eixo_x, eixo_y]

    if len(df_agr) < 2:
        st.warning("São necessários ao menos 2 pontos para traçar uma tendência.")
        st.markdown("---")
        return

    # Linha de tendência via Altair
    base = alt.Chart(df_agr).encode(
        x=alt.X(f"{eixo_x}:O", sort=None, title=eixo_x),
        y=alt.Y(f"{eixo_y}:Q", title=f"{agregacao} de {eixo_y}"),
        tooltip=[eixo_x, eixo_y],
    )

    linha    = base.mark_line(color="#4C9BE8", strokeWidth=2)
    pontos   = base.mark_circle(color="#4C9BE8", size=60)
    regressao = base.transform_regression(eixo_x, eixo_y).mark_line(
        color="orange", strokeDash=[6, 3], strokeWidth=1.5
    )

    chart = (linha + pontos + regressao).properties(height=320).interactive()
    st.altair_chart(chart, use_container_width=True)
    st.caption("🟠 Linha tracejada = tendência linear (regressão simples)")

    # Delta: primeiro vs último valor
    primeiro = df_agr[eixo_y].iloc[0]
    ultimo   = df_agr[eixo_y].iloc[-1]
    delta    = ultimo - primeiro
    pct      = (delta / primeiro * 100) if primeiro != 0 else 0
    sinal    = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"

    st.metric(
        f"{sinal} Variação do período",
        f"{ultimo:.2f}",
        delta=f"{delta:+.2f} ({pct:+.1f}%)",
    )

    st.markdown("---")