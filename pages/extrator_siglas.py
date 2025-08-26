import streamlit as st
import pandas as pd
import os
import fitz  # PyMuPDF
import io
import re

# CSS para estilização da página e do uploader
st.markdown("""
    <style>
    /* Tradução do file uploader */
    .stFileUploader > div:first-child::before {
        content: "Procurar arquivos";
    }
    .stFileUploader > div > [data-testid="stFileUploaderDropzone"]::after {
        content: "Arraste e solte o arquivo aqui";
    }
    
    /* Centralização de títulos */
    .centered-title {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Título da Página Principal
st.markdown('<h1 class="centered-title">🔠 Extrator de Siglas</h1>', unsafe_allow_html=True)
st.markdown("---")

# Upload de PDF
uploaded_files = st.file_uploader("Carregue seus PDFs para extrair as siglas", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    try:
        todos_dados = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Processar cada arquivo PDF
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processando {uploaded_file.name}...")
            
            pdf_bytes = uploaded_file.read()
            documento = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Percorrer todas as páginas do PDF
            for numero_pagina, pagina in enumerate(documento):
                texto = pagina.get_text()
                
                # Padrão regex para encontrar palavras em maiúsculas com 2 ou mais caracteres
                siglas = re.finditer(r'\b[A-Z][A-Z0-9-]{1,}\b', texto)
                
                for sigla in siglas:
                    sigla_texto = sigla.group()
                    # Define o contexto ao redor da sigla
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
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        # Criar e exibir DataFrame com os resultados
        if todos_dados:
            df = pd.DataFrame(todos_dados, columns=["Documento", "Página", "Sigla", "Contexto"])
            
            st.markdown("### Siglas Encontradas")
            st.dataframe(df)
            
            # Botão para download do Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name="siglas_extraidas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            status_text.success("✅ Processamento concluído!")
        else:
            st.warning("Nenhuma sigla foi encontrada nos arquivos PDF selecionados.")
            
        progress_bar.empty()
        
    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {str(e)}")
else:
    st.info("👆 Por favor, faça upload de um ou mais arquivos PDF para começar a extração.")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido para o TRE-BA")