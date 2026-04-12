import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import csv
import time
import os

from converter import (
    botao_download_customizado,
    gerar_vcf,
    gerar_excel_xlsx,
    gerar_csv,
    gerar_txt_emails,
)
from data_analysis import renderizar_analise

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Admin Data Tools Analytics",
    page_icon="📇",
    layout="centered"
)

# --- CARREGA O CSS EXTERNO ---
def injetar_css():
    if os.path.exists("static/style.css"):
        with open("static/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("Arquivo style.css não encontrado.")

    # O rodapé é HTML (conteúdo dinâmico), por isso fica aqui e não no CSS
    st.markdown(
        '<div class="footer">Desenvolvido por <b>Alessandro</b> | 2026</div>',
        unsafe_allow_html=True
    )

# --- CARREGA JS EXTERNO ---
def carregar_js(file_name, nome_da_funcao):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            js_code = f.read()
            js_completo = f"""
            <script>
            {js_code}

            // Dispara a função escolhida:
            {nome_da_funcao}();

            // Timestamp para driblar o cache: {time.time()}
            </script>
            """
            components.html(js_completo, height=0)
    else:
        st.error(f"Arquivo {file_name} não encontrado.")

# --- SCROLL AUTOMÁTICO ---
def rolar_para_botoes():
    st.markdown("<div id='alvo-scroll'></div>", unsafe_allow_html=True)
    carregar_js("static/script.js", "fazerScroll")

# --- INTERFACE PRINCIPAL ---
def main():
    injetar_css()

    if "arquivo_bytes" not in st.session_state: st.session_state.arquivo_bytes = None
    if "nome_arquivo" not in st.session_state: st.session_state.nome_arquivo = ""
    if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
    if "df_atual" not in st.session_state: st.session_state.df_atual = None
    if "fazer_scroll" not in st.session_state: st.session_state.fazer_scroll = False

    col_img, col_txt = st.columns([0.7, 6], gap="small")
    with col_img:
        st.image("https://cdn-icons-png.flaticon.com/512/8112/8112512.png", width=55)
    with col_txt:
        st.markdown("### Admin Data Tools Analytics")
        st.markdown("Ferramenta para converter e analisar dados de planilhas.")

    st.write("")
    opcoes_menu = ["🔄 Conversor de Arquivos", "📊 Análise de Dados", "ℹ️ Sobre o Sistema"]
    menu = st.radio("Navegação:", opcoes_menu, horizontal=True, label_visibility="collapsed")
    st.markdown('<hr style="margin: 8px 0px;">', unsafe_allow_html=True)

    # ---- ABA: CONVERSOR ----
    if menu == "🔄 Conversor de Arquivos":
        st.markdown("Faça o upload da sua planilha para gerar os arquivos compatíveis.")
        arquivo_carregado = st.file_uploader(
            "Arraste seu arquivo CSV ou Excel aqui:",
            type=["csv", "xlsx", "xls"],
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if arquivo_carregado is not None:
            if st.session_state.nome_arquivo != arquivo_carregado.name:
                st.session_state.fazer_scroll = True
            st.session_state.arquivo_bytes = arquivo_carregado.getvalue()
            st.session_state.nome_arquivo = arquivo_carregado.name

        if st.session_state.arquivo_bytes is not None:
            if st.button("🗑️ Limpar Arquivo"):
                st.session_state.arquivo_bytes = None
                st.session_state.nome_arquivo = ""
                st.session_state.df_atual = None
                st.session_state.uploader_key += 1
                st.session_state.fazer_scroll = False
                st.rerun()

            extensao = st.session_state.nome_arquivo.split('.')[-1].lower()
            df = None

            try:
                if extensao == 'csv':
                    try:
                        conteudo_texto = st.session_state.arquivo_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        conteudo_texto = st.session_state.arquivo_bytes.decode("latin-1")
                    separador_adivinhado = csv.Sniffer().sniff(conteudo_texto[:2048]).delimiter
                    df = pd.read_csv(io.StringIO(conteudo_texto), sep=separador_adivinhado, dtype=str)

                elif extensao in ['xlsx', 'xls']:
                    df = pd.read_excel(io.BytesIO(st.session_state.arquivo_bytes), dtype=str)

                if df is not None:
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    dicionario_colunas = {
                        "nome completo": "nome", "cliente": "nome", "nome do cliente": "nome",
                        "nome fantasia": "nome", "razao social": "nome", "razão social": "nome",
                        "primeiro nome": "nome", "name": "nome", "first name": "nome", "nombre": "nome",
                        "contato": "telefone", "celular": "telefone", "cel": "telefone",
                        "whatsapp": "telefone", "whats": "telefone", "zap": "telefone",
                        "tel": "telefone", "fone": "telefone", "telefone 1": "telefone",
                        "celular 1": "telefone", "telefone de contato": "telefone", "numero": "telefone",
                        "número": "telefone", "phone": "telefone", "mobile": "telefone",
                        "e-mail": "email", "e mail": "email", "mail": "email",
                        "endereço de email": "email", "endereço de e-mail": "email",
                        "email address": "email", "correio eletronico": "email",
                        "correio eletrônico": "email", "correo": "email"
                    }
                    df = df.rename(columns=dicionario_colunas)
                    st.session_state.df_atual = df

            except Exception as e:
                st.error(f"❌ Erro ao ler a planilha. Tente abrir o arquivo e salvá-lo novamente como CSV. Detalhe: {e}")

            if df is not None:
                st.markdown("#### 📥 Escolha o formato de saída:")
                nome_base = st.session_state.nome_arquivo.rsplit('.', 1)[0]

                try:
                    col1, col2 = st.columns(2)
                    with col1:
                        bytes_vcf = gerar_vcf(df)
                        botao_download_customizado("📱 Contatos (VCF)", bytes_vcf, f"{nome_base}.vcf", "text/vcard", "#00D1FF", "black")
                    with col2:
                        bytes_xlsx = gerar_excel_xlsx(df)
                        botao_download_customizado("📊 Excel (.xlsx)", bytes_xlsx, f"{nome_base}_convertido.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "#4CAF50")

                    col3, col4 = st.columns(2)
                    with col3:
                        bytes_csv = gerar_csv(df)
                        botao_download_customizado("📑 Arquivo CSV", bytes_csv, f"{nome_base}_convertido.csv", "text/csv", "#FF9800")
                    with col4:
                        bytes_emails = gerar_txt_emails(df)
                        botao_download_customizado("📧 E-mails (.txt)", bytes_emails, f"{nome_base}_emails.txt", "text/plain", "#AF47FF")

                except Exception as e:
                    st.error(f"❌ Erro ao processar os arquivos finais. Detalhe: {e}")

            if st.session_state.fazer_scroll:
                rolar_para_botoes()
                st.session_state.fazer_scroll = False

    # ---- ABA: ANÁLISE ----
    elif menu == "📊 Análise de Dados":
        renderizar_analise()

    # ---- ABA: SOBRE ----
    elif menu == "ℹ️ Sobre o Sistema":
        st.markdown("""
        Este sistema foi criado para facilitar a vida de quem precisa gerenciar dados de planilhas.

        **Como funciona:**
        1. Envie um arquivo `.csv`, `.xlsx` ou `.xls`.
        2. O sistema lê os dados de forma segura na memória.
        3. O conversor possibilita escolher o formato para baixar (VCF, XLSX, CSV ou TXT).
        4. Acesse a aba **Análise de Dados** para extrair insights da sua planilha.
        """)

if __name__ == "__main__":
    main()