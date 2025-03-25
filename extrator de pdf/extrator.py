import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
from PIL import Image
import fitz  # PyMuPDF
from collections import defaultdict
import io
import re

# Configuração da página
# Carregar o ícone da página
icon_path = os.path.join("imagens", "tre_ba.png")
if os.path.exists(icon_path):
    icon = Image.open(icon_path)
else:
    icon = "📊"

st.set_page_config(
    page_title="Extrator de PDF",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para traduzir o file uploader
st.markdown("""
    <style>
    /* Tradução do file uploader */
    .stFileUploader > div:first-child {
        color: transparent;
    }
    .stFileUploader > div:first-child::before {
        content: "Procurar arquivos";
        color: black;
    }
    .stFileUploader > div:first-child::after {
        content: "Arraste e solte o arquivo aqui";
        color: black;
    }
    
    /* Centralização de títulos */
    .centered-title {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:    
    # Logo
    logo_path = os.path.join("imagens", "tre_ba_completo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.image("https://via.placeholder.com/200x80?text=TRE-BA", width=200)
    
    st.markdown("---")
    st.markdown('<h3 class="centered-title">Menu</h3>', unsafe_allow_html=True)
    page = st.radio(
        "Selecione uma opção:",
        ["🏠 Página Inicial", "🔗🌍 Extrator de Links", "🔠 Extrator de Siglas (não concluído)"]
    )
    st.markdown("---")
    st.markdown('<h3 class="centered-title">Alterar tema</h3>', unsafe_allow_html=True)
    st.markdown("💡 Para trocar de tema, vá no canto superior direito em ⋮ e em seguida em Settings/Configurações")

# Área principal
if page == "🏠 Página Inicial":
    # Cabeçalho
    st.markdown('<h1 class="centered-title">🔍 Extrator de Links/Siglas 🔍</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Seção de introdução
    col1, col2 = st.columns([1, 2])
    with col2:
        st.markdown("""
        <h3 class="centered-title">Como Usar</h3>
        
        1. Navegue até a aba "Extrator de Links" ou "Extrator de Siglas" no menu lateral esquerdo
        2. Faça upload de um ou mais arquivos PDF
        3. O sistema irá extrair automaticamente todos os links/siglas encontrados nos PDFs
        4. Um arquivo Excel será gerado com os seguintes dados:
           - Nome do documento
           - Número da página
           - Texto associado ao link/URL do link Ou Sigla
        5. Você poderá visualizar os resultados na tela e fazer o download do arquivo Excel em "📥 Download Excel"
        """, unsafe_allow_html=True)
    with col1:
        banner_path = os.path.join("imagens", "tre_ba.png")
        if os.path.exists(banner_path):
            st.image(banner_path, width=300)
        else:
            st.image("https://via.placeholder.com/300x200?text=TRE-BA", width=300)

elif page == "🔗🌍 Extrator de Links":
    st.markdown('<h1 class="centered-title">🔗🌍 Extrator de Links</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Upload de PDF
    uploaded_files = st.file_uploader("Carregue seus PDFs", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        try:
            # Lista para armazenar todos os dados
            todos_dados = []
            
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Processar cada arquivo PDF
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processando {uploaded_file.name}...")
                
                # Ler o arquivo PDF
                pdf_bytes = uploaded_file.read()
                documento = fitz.open(stream=pdf_bytes, filetype="pdf")
                
                # Dicionário para armazenar os hiperlinks e seus textos combinados por página
                dicionario_links = defaultdict(lambda: defaultdict(str))
                
                # Percorrer todas as páginas do PDF
                for numero_pagina in range(len(documento)):
                    for link in documento[numero_pagina].get_links():
                        if "uri" in link:
                            retangulo = link["from"]
                            texto = documento[numero_pagina].get_text("text", clip=retangulo).strip()
                            url = link["uri"]
                            dicionario_links[numero_pagina + 1][url] += " " + texto if dicionario_links[numero_pagina + 1][url] else texto
                
                # Adicionar dados do arquivo atual à lista geral
                for pagina, urls in dicionario_links.items():
                    for url, texto in urls.items():
                        todos_dados.append([uploaded_file.name, pagina, texto.strip(), url])
                
                documento.close()
                
                # Atualizar barra de progresso
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            # Criar DataFrame do pandas com todos os dados
            if todos_dados:
                df = pd.DataFrame(todos_dados, columns=["Documento", "Página", "Texto", "URL"])
                
                # Mostrar os dados na tela
                st.markdown("### Links Encontrados")
                st.dataframe(df)
                
                # Criar botão para download do Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                excel_data = excel_buffer.getvalue()
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="links_extraidos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                status_text.text("✅ Processamento concluído!")
            else:
                st.warning("Nenhum link foi encontrado nos arquivos PDF selecionados.")
            
            # Limpar barra de progresso
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {str(e)}")
    else:
        st.info("👆 Por favor, faça upload de um ou mais arquivos PDF para começar a extração.")

elif page == "🔠 Extrator de Siglas (não concluído)":
    st.markdown('<h1 class="centered-title">🔠 Extrator de Siglas (não concluído)</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Upload de PDF
    uploaded_files = st.file_uploader("Carregue seus PDFs", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        try:
            # Lista para armazenar todos os dados
            todos_dados = []
            
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Processar cada arquivo PDF
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processando {uploaded_file.name}...")
                
                # Ler o arquivo PDF
                pdf_bytes = uploaded_file.read()
                documento = fitz.open(stream=pdf_bytes, filetype="pdf")
                
                # Percorrer todas as páginas do PDF
                for numero_pagina in range(len(documento)):
                    # Obter o texto da página
                    pagina = documento[numero_pagina]
                    texto = pagina.get_text()
                    
                    # Encontrar siglas (palavras em maiúsculas com 2 ou mais letras)
                    # Padrão: palavra em maiúsculas, pode conter números e hífens
                    siglas = re.finditer(r'\b[A-Z][A-Z0-9-]{1,}\b', texto)
                    
                    for sigla in siglas:
                        sigla_texto = sigla.group()
                        # Pegar um contexto ao redor da sigla (100 caracteres antes e depois)
                        inicio = max(0, sigla.start() - 100)
                        fim = min(len(texto), sigla.end() + 100)
                        contexto = texto[inicio:fim].replace('\n', ' ').strip()
                        
                        todos_dados.append([
                            uploaded_file.name,
                            numero_pagina + 1,
                            sigla_texto,
                            contexto
                        ])
                
                documento.close()
                
                # Atualizar barra de progresso
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            # Criar DataFrame do pandas com todos os dados
            if todos_dados:
                df = pd.DataFrame(todos_dados, columns=["Documento", "Página", "Sigla", "Contexto"])
                
                # Mostrar os dados na tela
                st.markdown("### Siglas Encontradas")
                st.dataframe(df)
                
                # Criar botão para download do Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                excel_data = excel_buffer.getvalue()
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="siglas_extraidas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                status_text.text("✅ Processamento concluído!")
            else:
                st.warning("Nenhuma sigla foi encontrada nos arquivos PDF selecionados.")
            
            # Limpar barra de progresso
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {str(e)}")
    else:
        st.info("👆 Por favor, faça upload de um ou mais arquivos PDF para começar a extração.")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido para o TRE-BA") 