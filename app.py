import streamlit as st
import os
from PIL import Image


icon_path = os.path.join("images", "tre_ba.png")
icon = Image.open(icon_path)

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA STREAMLIT
st.set_page_config(
    page_title="Streamlit do TRE-BA",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

paginas = {
    "": [
        st.Page("pages/home_page.py", title="Página Inicial", icon="🏠", default=True)
    ],
    "Funcionalidades": [
        st.Page("pages/extrator_de_links.py", title="Extrator de Links (RG)", icon="🔗"),
        st.Page("pages/extrator_siglas.py", title="Extrator de Siglas (RG)", icon="🔤"),
        st.Page("pages/extracao_metas_tre_ba.py", title="Extrator de Metas", icon="🎯"),
        st.Page("pages/processador_ids.py", title="Processador de IDS", icon="🌴")
    ],
    "Contato": [
        st.Page("pages/fale_conosco.py", title="Fale Conosco", icon="📬")
    ],
}

# Executar a página selecionada
pg = st.navigation(paginas)
pg.run()

