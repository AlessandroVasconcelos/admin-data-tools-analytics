import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import base64
import csv
import time
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestor de Contatos", 
    page_icon="📇", 
    layout="centered"
)

# --- NOVA FUNÇÃO PARA CARREGAR JS EXTERNO ---
def carregar_js(file_name, nome_da_funcao):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            js_code = f.read()
            
            # Ele lê todo o script.js, mas só executa a função que você pediu!
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

# --- FUNÇÃO DE SCROLL AUTOMÁTICO ENXUTA ---
def rolar_para_botoes():
    # 1. Cria o alvo invisível na tela
    st.markdown("<div id='alvo-scroll'></div>", unsafe_allow_html=True)
    
    # 2. Chama a função JavaScript do arquivo externo
    carregar_js("script.js", "fazerScroll")

# --- BOTÃO DE DOWNLOAD CUSTOMIZADO HTML ---
def botao_download_customizado(label, data, file_name, mime_type, cor_fundo, cor_texto="white"):
    b64 = base64.b64encode(data).decode()
    html = f'''
    <a href="data:{mime_type};base64,{b64}" download="{file_name}" 
       style="display: block; width: 100%; background-color: {cor_fundo}; color: {cor_texto}; text-align: center; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; font-family: sans-serif; font-size: 1rem; border: 1px solid rgba(0,0,0,0.1); margin-bottom: 10px; box-sizing: border-box; transition: opacity 0.2s;"
       onMouseOver="this.style.opacity='0.8'"
       onMouseOut="this.style.opacity='1'">
       {label}
    </a>
    '''
    st.markdown(html, unsafe_allow_html=True)

# --- FUNÇÕES DE CONVERSÃO NA MEMÓRIA ---
def gerar_vcf(df):
    vcf_output = io.StringIO()
    df = df.fillna("") 
    for index, row in df.iterrows():
        nome = str(row.get("nome", "")).strip()
        telefone = str(row.get("telefone", "")).strip()
        email = str(row.get("email", "")).strip()
        if not nome: 
            continue
        vcf_output.write("BEGIN:VCARD\nVERSION:3.0\n")
        vcf_output.write(f"N:{nome};;;;\nFN:{nome}\n")
        if telefone:
            vcf_output.write(f"TEL;TYPE=CELL:{telefone}\n")
        if email:
            vcf_output.write(f"EMAIL:{email}\n")
        vcf_output.write("END:VCARD\n\n")
    return vcf_output.getvalue().encode('utf-8')

def gerar_excel_xlsx(df):
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    return output.getvalue()

def gerar_csv(df):
    return df.to_csv(index=False, sep=",").encode('utf-8')

def gerar_txt_emails(df):
    df = df.fillna("")
    if "email" not in df.columns:
        return "Nenhum e-mail encontrado. Verifique se a coluna se chama 'email'.".encode('utf-8')
    lista_emails = [str(email).strip() for email in df["email"] if str(email).strip() != ""]
    texto_final = "\n".join(lista_emails) if lista_emails else "Nenhum e-mail válido encontrado."
    return texto_final.encode('utf-8')

# --- ESTILIZAÇÃO CSS (RODAPÉ E MENU) ---
def injetar_css():
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] {display: none !important;}
        [data-testid="stSidebar"] {display: none !important;}

        div[data-testid="stHorizontalBlock"] div.stButton button {
            border-color: transparent !important;
            background-color: transparent !important;
            border-radius: 0px !important;
            border-bottom: 2px solid transparent !important;
            padding-bottom: 5px !important;
            margin-right: 20px !important;
        }
        div[data-testid="stHorizontalBlock"] div.stButton button[kind="secondaryFormSubmit"] {
            border-bottom: 2px solid var(--primary-color) !important;
            color: var(--primary-color) !important;
        }
        div[data-testid="stHorizontalBlock"] div.stButton button:hover {
            color: var(--primary-color) !important;
        }

        .footer {
            position: fixed !important; left: 0 !important; bottom: 0 !important; width: 100% !important;
            background-color: var(--secondary-background-color, #0e1117) !important;
            color: #aaaaaa !important; text-align: center !important; padding: 10px !important; 
            font-size: 14px !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important; 
            z-index: 999999 !important; opacity: 1 !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        <div class="footer">Desenvolvido por <b>Alessandro</b> | 2026</div>
    """, unsafe_allow_html=True)

# --- MENU E INTERFACE PRINCIPAL ---
def main():
    injetar_css() 

    if "arquivo_bytes" not in st.session_state: st.session_state.arquivo_bytes = None
    if "nome_arquivo" not in st.session_state: st.session_state.nome_arquivo = ""
    if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0 
    if "df_atual" not in st.session_state: st.session_state.df_atual = None
    if "fazer_scroll" not in st.session_state: st.session_state.fazer_scroll = False

    col_img, col_txt = st.columns([1, 6])
    with col_img:
        st.image("https://cdn-icons-png.flaticon.com/512/8112/8112512.png", width=60)
    with col_txt:
        st.markdown("### Admin Data Tools Analytics")
        st.markdown("Ferramenta para converter e analisar dados de planilhas.")

    st.write("") 
    opcoes_menu = ["🔄 Conversor de Arquivos", "📊 Análise de Dados", "ℹ️ Sobre o Sistema"]
    menu = st.radio("Navegação:", opcoes_menu, horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if menu == "🔄 Conversor de Arquivos":
        st.markdown("Faça o upload da sua planilha para gerar os arquivos compatíveis.")
        arquivo_carregado = st.file_uploader("Arraste seu arquivo CSV ou Excel aqui:", type=["csv", "xlsx", "xls"], key=f"uploader_{st.session_state.uploader_key}")

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

            # Aciona a função visual de descer a página se a flag estiver ativada
            if st.session_state.fazer_scroll:
                rolar_para_botoes()
                st.session_state.fazer_scroll = False

    elif menu == "📊 Análise de Dados":
        if st.session_state.df_atual is None:
            st.warning("⚠️ Nenhuma planilha carregada! Por favor, vá em 'Conversor de Arquivos' e faça o upload primeiro.")
        else:
            df = st.session_state.df_atual.copy()
            st.markdown("### 👁️ Pré-visualização dos Dados")
            st.dataframe(df, use_container_width=True, height=200)
            st.markdown("---")
            st.markdown("### 🎯 Resumo da Base de Contatos")
            col1, col2, col3 = st.columns(3)
            total_linhas = len(df)
            col1.metric("Total de Contatos", total_linhas)
            qtd_telefone = df['telefone'].dropna().replace("", pd.NA).count() if 'telefone' in df.columns else 0
            qtd_email = df['email'].dropna().replace("", pd.NA).count() if 'email' in df.columns else 0
            col2.metric("Com Telefone", f"{qtd_telefone} ({(qtd_telefone/total_linhas)*100:.1f}%)" if total_linhas > 0 else "0")
            col3.metric("Com E-mail", f"{qtd_email} ({(qtd_email/total_linhas)*100:.1f}%)" if total_linhas > 0 else "0")
            st.markdown("---")
            st.markdown("### 📧 Provedores de E-mail mais usados")
            if 'email' in df.columns and qtd_email > 0:
                dominios = df['email'].dropna().astype(str).apply(lambda x: x.split('@')[-1] if '@' in x else None)
                top_dominios = dominios.value_counts().head(10)
                st.bar_chart(top_dominios)
            else:
                st.info("A coluna 'email' não foi encontrada ou está vazia.")
            st.markdown("---")
            st.markdown("### 📈 Análise Dinâmica")
            st.write("Escolha qualquer coluna da sua planilha para visualizar a distribuição dos dados:")
            coluna_escolhida = st.selectbox("Selecione a coluna:", df.columns)
            if coluna_escolhida:
                dados_limpos = df[coluna_escolhida].replace("", pd.NA).dropna()
                if len(dados_limpos) == 0:
                    st.warning("Esta coluna está vazia.")
                elif len(dados_limpos.unique()) > 50:
                    st.warning("Existem muitos valores diferentes nesta coluna (ex: nomes próprios). O gráfico ficaria ilegível.")
                else:
                    contagem = dados_limpos.value_counts().head(15)
                    st.bar_chart(contagem)

    elif menu == "ℹ️ Sobre o Sistema":
        st.markdown("""
        Este sistema foi criado para facilitar a vida de quem precisa gerenciar dados de planilhas.
        
        **Como funciona:**
        1. Envie um arquivo `.csv`, `.xlsx` ou `.xls` com as colunas `nome`, `telefone` e `email`.
        2. O sistema lê os dados de forma segura na memória.
        3. O conversor possibilita escolher o formato para baixar (VCF, XLSX, CSV ou TXT).
        4. Acesse a aba **Análise de Dados** para extrair insights da sua lista.
        """)

if __name__ == "__main__":
    main()
