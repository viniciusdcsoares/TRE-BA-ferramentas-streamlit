import streamlit as st
import os
from PIL import Image

#base_path_pc = r"C:\Users\159710740507\Documents\..."
#icon_path_pc = os.path.join(base_path, "imagens", "tre_ba.png")
icon_path = os.path.join("extrator de pdf", "imagens", "tre_ba.png")
icon = Image.open(icon_path)

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA STREAMLIT
st.set_page_config(
    page_title="Streamlit do TERRAS",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

paginas = {
    "": [
        st.Page(os.path.join(base_path, "paginas/home_page.py"), title="Página Inicial", icon="🏠", default=True)
    ],
    "Funcionalidades": [
        st.Page(os.path.join(base_path, "paginas/extrator_de_links.py"), title="Extrator de Links (RG)", icon="🔗"),
        st.Page(os.path.join(base_path, "paginas/extrator_siglas.py"), title="Extrator de Siglas (RG)", icon="🔤"),
        st.Page(os.path.join(base_path, "paginas/extracao_metas_tre_ba.py"), title="Extrator de Metas", icon="🎯"),
        st.Page(os.path.join(base_path, "paginas/processador_ids.py"), title="Processador de IDS", icon="🌴")
    ],
    "Contato": [
        st.Page(os.path.join(base_path, "paginas/fale_conosco.py"), title="Fale Conosco", icon="📬")
    ],
}

# Executar a página selecionada
pg = st.navigation(paginas)
pg.run()
