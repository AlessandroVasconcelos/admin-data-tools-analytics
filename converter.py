import io
import base64
import streamlit as st


# --- BOTÃO DE DOWNLOAD CUSTOMIZADO ---
def botao_download_customizado(label, data, file_name, mime_type, cor_fundo, cor_texto="white"):
    b64 = base64.b64encode(data).decode()
    html = f'''
    <a href="data:{mime_type};base64,{b64}"
       download="{file_name}"
       class="botao-download"
       style="background-color: {cor_fundo}; color: {cor_texto};">
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