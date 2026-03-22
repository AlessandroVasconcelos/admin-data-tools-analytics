import streamlit as st
import pandas as pd
import csv
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor de Contatos", page_icon="📇", layout="centered")

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

# --- ESTILIZAÇÃO CSS (RODAPÉ) ---
def injetar_css():
    st.markdown("""
        <style>
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: transparent; color: #888888; text-align: center;
            padding: 10px; font-size: 14px; border-top: 1px solid #eaeaea; z-index: 100;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        <div class="footer">Desenvolvido por <b>Alessandro Vasconcelos</b> | 2026</div>
    """, unsafe_allow_html=True)

# --- MENU E INTERFACE PRINCIPAL ---
def main():
    injetar_css() 

    # --- INICIALIZAÇÃO DA MEMÓRIA ---
    if "arquivo_bytes" not in st.session_state:
        st.session_state.arquivo_bytes = None
    if "nome_arquivo" not in st.session_state:
        st.session_state.nome_arquivo = ""
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0 
    # Nova memória para guardar os dados e enviar para os gráficos
    if "df_atual" not in st.session_state:
        st.session_state.df_atual = None

    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8112/8112512.png", width=100)
    st.sidebar.title("Navegação")
    # Adicionamos a nova opção de Análise no Menu
    menu = st.sidebar.radio("Ir para:", ["🔄 Conversor de Arquivos", "📊 Análise de Dados", "ℹ️ Sobre o Sistema"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("Ferramenta para converter planilhas de contatos e analisar dados.")

    # ==========================================
    # PÁGINA 1: CONVERSOR
    # ==========================================
    if menu == "🔄 Conversor de Arquivos":
        st.title("📇 Conversor de Contatos")
        st.markdown("Faça o upload da sua planilha para gerar os arquivos compatíveis.")
        
        arquivo_carregado = st.file_uploader(
            "Arraste seu arquivo CSV ou Excel aqui", 
            type=["csv", "xlsx", "xls"],
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if arquivo_carregado is not None:
            st.session_state.arquivo_bytes = arquivo_carregado.getvalue()
            st.session_state.nome_arquivo = arquivo_carregado.name

        if st.session_state.arquivo_bytes is not None:
            st.success(f"Arquivo **{st.session_state.nome_arquivo}** carregado com sucesso!")
            
            if st.button("🗑️ Limpar Arquivo e Enviar Outro"):
                st.session_state.arquivo_bytes = None
                st.session_state.nome_arquivo = ""
                st.session_state.df_atual = None # Limpa a tabela da memória também
                st.session_state.uploader_key += 1 
                st.rerun() 
            
            st.markdown("---")

            extensao = st.session_state.nome_arquivo.split('.')[-1].lower()
            df = None

            try:
                if extensao == 'csv':
                    with st.expander("⚙️ Configurações do CSV", expanded=True):
                        separador = st.selectbox("Qual é o separador das colunas?", [",", ";", "|", "\t"])
                    try:
                        conteudo_texto = st.session_state.arquivo_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        conteudo_texto = st.session_state.arquivo_bytes.decode("latin-1")
                    df = pd.read_csv(io.StringIO(conteudo_texto), sep=separador, dtype=str)
                
                elif extensao in ['xlsx', 'xls']:
                    df = pd.read_excel(io.BytesIO(st.session_state.arquivo_bytes), dtype=str)
                
                if df is not None:
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    # Salva a tabela pronta na memória para a tela de Gráficos usar
                    st.session_state.df_atual = df

            except Exception as e:
                st.error(f"❌ Erro ao ler a planilha. Detalhe: {e}")

            if df is not None:
                st.markdown("### 👁️ Pré-visualização dos Dados")
                st.dataframe(df, use_container_width=True, height=200)
                st.caption(f"Total de registros encontrados: {len(df)}")

                st.markdown("---")
                st.markdown("### 📥 Escolha o formato de saída:")
                
                nome_base = st.session_state.nome_arquivo.rsplit('.', 1)[0]

                try:
                    col1, col2 = st.columns(2)
                    with col1:
                        bytes_vcf = gerar_vcf(df)
                        st.download_button("📱 Contatos (VCF)", data=bytes_vcf, file_name=f"{nome_base}.vcf", mime="text/vcard", use_container_width=True, type="primary")
                    with col2:
                        bytes_xlsx = gerar_excel_xlsx(df)
                        st.download_button("📊 Excel (.xlsx)", data=bytes_xlsx, file_name=f"{nome_base}_convertido.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="secondary")

                    col3, col4 = st.columns(2)
                    with col3:
                        bytes_csv = gerar_csv(df)
                        st.download_button("📑 Arquivo CSV", data=bytes_csv, file_name=f"{nome_base}_convertido.csv", mime="text/csv", use_container_width=True, type="secondary")
                    with col4:
                        bytes_emails = gerar_txt_emails(df)
                        st.download_button("📧 E-mails (.txt)", data=bytes_emails, file_name=f"{nome_base}_emails.txt", mime="text/plain", use_container_width=True, type="secondary")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao processar os arquivos finais. Detalhe: {e}")

    # ==========================================
    # PÁGINA 2: ANÁLISE DE DADOS (NOVA)
    # ==========================================
    elif menu == "📊 Análise de Dados":
        st.title("📊 Análise de Dados e Gráficos")
        
        # Verifica se o usuário já carregou uma planilha na primeira aba
        if st.session_state.df_atual is None:
            st.warning("⚠️ Nenhuma planilha carregada! Por favor, vá em 'Conversor de Arquivos' e faça o upload primeiro.")
        else:
            df = st.session_state.df_atual.copy()
            
            # --- SEÇÃO 1: MÉTRICAS GERAIS ---
            st.markdown("### 🎯 Resumo da Base de Contatos")
            col1, col2, col3 = st.columns(3)
            
            total_linhas = len(df)
            col1.metric("Total de Contatos", total_linhas)
            
            # Calcula quantos têm telefone e e-mail (se as colunas existirem)
            qtd_telefone = df['telefone'].dropna().replace("", pd.NA).count() if 'telefone' in df.columns else 0
            qtd_email = df['email'].dropna().replace("", pd.NA).count() if 'email' in df.columns else 0
            
            col2.metric("Com Telefone", f"{qtd_telefone} ({(qtd_telefone/total_linhas)*100:.1f}%)" if total_linhas > 0 else "0")
            col3.metric("Com E-mail", f"{qtd_email} ({(qtd_email/total_linhas)*100:.1f}%)" if total_linhas > 0 else "0")

            st.markdown("---")

            # --- SEÇÃO 2: GRÁFICO DE PROVEDORES DE E-MAIL ---
            st.markdown("### 📧 Provedores de E-mail mais usados")
            if 'email' in df.columns and qtd_email > 0:
                # Extrai apenas o domínio (o que vem depois do @)
                dominios = df['email'].dropna().astype(str).apply(lambda x: x.split('@')[-1] if '@' in x else None)
                top_dominios = dominios.value_counts().head(10) # Pega os 10 maiores
                
                st.bar_chart(top_dominios)
            else:
                st.info("A coluna 'email' não foi encontrada ou está vazia.")

            st.markdown("---")

            # --- SEÇÃO 3: ANÁLISE DINÂMICA (GRÁFICO LIVRE) ---
            st.markdown("### 📈 Análise Dinâmica")
            st.write("Escolha qualquer coluna da sua planilha para visualizar a distribuição dos dados:")
            
            # Deixa o usuário escolher a coluna
            coluna_escolhida = st.selectbox("Selecione a coluna:", df.columns)
            
            if coluna_escolhida:
                # Remove valores vazios para não sujar o gráfico
                dados_limpos = df[coluna_escolhida].replace("", pd.NA).dropna()
                
                if len(dados_limpos) == 0:
                    st.warning("Esta coluna está vazia.")
                elif len(dados_limpos.unique()) > 50:
                    st.warning("Existem muitos valores diferentes nesta coluna (ex: nomes próprios). O gráfico ficaria ilegível.")
                else:
                    # Conta a frequência e mostra o gráfico
                    contagem = dados_limpos.value_counts().head(15) # Top 15
                    st.bar_chart(contagem)


    # ==========================================
    # PÁGINA 3: SOBRE
    # ==========================================
    elif menu == "ℹ️ Sobre o Sistema":
        st.title("ℹ️ Sobre")
        st.markdown("""
        Bem-vindo ao **Gestor de Contatos**!
        
        Este sistema foi criado para facilitar a vida de quem precisa gerenciar grandes listas de contatos.
        
        **Como funciona:**
        1. Envie um arquivo `.csv`, `.xlsx` ou `.xls` com as colunas `nome`, `telefone` e `email`.
        2. O sistema lê os dados de forma segura na memória.
        3. Acesse a aba **Análise de Dados** para extrair insights da sua lista.
        4. Volte ao conversor e escolha o formato para baixar (VCF, XLSX, CSV ou TXT).
        
        ---
        **Desenvolvido por:** Alessandro Vasconcelos
        """)

if __name__ == "__main__":
    main()