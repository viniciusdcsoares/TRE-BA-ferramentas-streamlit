import streamlit as st
import pandas as pd
import os
import fitz  # PyMuPDF
from collections import defaultdict
import io

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
st.markdown('<h1 class="centered-title">🔗🌍 Extrator de Links</h1>', unsafe_allow_html=True)
st.markdown("---")

# Upload de PDF
uploaded_files = st.file_uploader("Carregue seus PDFs para extrair os links", type=['pdf'], accept_multiple_files=True)

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
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        # Criar e exibir DataFrame com os resultados
        if todos_dados:
            df = pd.DataFrame(todos_dados, columns=["Documento", "Página", "Texto", "URL"])
            
            st.markdown("### Links Encontrados")
            st.dataframe(df)
            
            # Botão para download do Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name="links_extraidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            status_text.success("✅ Processamento concluído!")
        else:
            st.warning("Nenhum link foi encontrado nos arquivos PDF selecionados.")
            
        progress_bar.empty()
        
    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {str(e)}")
else:
    st.info("👆 Por favor, faça upload de um ou mais arquivos PDF para começar a extração.")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido para o TRE-BA")