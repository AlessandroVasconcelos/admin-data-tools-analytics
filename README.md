## 📊 Admin Data Tools Analytics

<p align="justify">
Ferramenta administrativa desenvolvida para facilitar a manipulação, conversão e análise de planilhas. Com uma interface intuitiva, o sistema permite que usuários processem arquivos de forma automatizada, gerando arquivos prontos para importação em dispositivos móveis e dashboards estatísticos em tempo real.
</p>
🔗 Acesse a aplicação: https://app-data-tools-analytics.streamlit.app

---

### 📋 Funcionalidades Principais

🔄 Conversão Inteligente de Arquivos
- Upload de arquivos `.csv`, `.xlsx` e `.xls`
- Detecção automática de separadores em arquivos CSV
- Padronização automática de nomes de colunas (Nome, Telefone, E-mail)
- Uso de dicionário de sinônimos para normalização de dados

📥 Exportação Multi-formato
- Geração de arquivos **VCF (vCard)** para importação em contatos (celular/Google Contacts)
- Conversão para **Excel (.xlsx)** e **CSV**
- Extração de listas de e-mails em formato **.txt**
  
📊 Dashboard de Análise de Dados
- Métricas gerais da base:
  - Total de contatos
  - Percentual de contatos com telefone
  - Percentual de contatos com e-mail
- Análise dos provedores de e-mail mais utilizados
- Gráficos dinâmicos com distribuição por qualquer coluna

## 🚀 Como Rodar o Projeto Localmente

Este projeto foi desenvolvido em **Python** utilizando a biblioteca **Streamlit**.

### ⚙️ Passo a Passo

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/admin-data-tools-analytics.git
cd admin-data-tools-analytics
```
Windows:
```bash
venv\Scripts\activate
```
Linux/Mac:
```bash
source venv/bin/activate
```

---

3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

4. Execute a aplicação

```bash
streamlit run app.py
```

---

## 🌐 Acesso local

A aplicação será aberta automaticamente no navegador:

👉 http://localhost:8501

---

## 🛠️ Tecnologias Utilizadas
<a href="https://www.python.org/" style="text-decoration:none;"><img src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white"></a> 
<a href="https://streamlit.io/" style="text-decoration:none;"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"></a>
<a href="https://pandas.pydata.org/" style="text-decoration:none;"><img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"></a>
<a href="https://openpyxl.readthedocs.io/" style="text-decoration:none;"><img src="https://img.shields.io/badge/OpenPyXL-1F6FEB?style=for-the-badge&logo=microsoft-excel&logoColor=white"></a>
<a href="https://xlrd.readthedocs.io/" style="text-decoration:none;"><img src="https://img.shields.io/badge/xlrd-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white"></a>

