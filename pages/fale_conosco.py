import streamlit as st
import base64
import os
import smtplib
from email.message import EmailMessage
import tempfile
import re 

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

st.markdown('<h1 class="centered-title">📬 Fale Conosco</h1>', unsafe_allow_html=True)

def enviar_emails(senha, remetente, destinatarios, assunto, corpo_base, anexos):
    for destinatario in destinatarios:
        nome_destinatario = destinatario["nome"]
        email_destinatario = destinatario["email"]

        # Cria o objeto e-mail e atribui assunto, remetente e email do destinatario
        email = EmailMessage()
        email["Subject"] = assunto
        email["From"] = remetente
        email["To"] = email_destinatario

        # Corpo do e-mail (personalizado pelo nome do destinatário)
        corpo = corpo_base.format(nome=nome_destinatario)
        email.set_content(corpo)

        # Carregando os anexos
        for caminho_anexo in anexos:
            with open(caminho_anexo, "rb") as f:
                # Carregando o arquivo (em binario) e o nome do arquivo
                arquivo = f.read()
                nome_arquivo = os.path.basename(caminho_anexo)
                # Adicionando o anexo
                email.add_attachment(arquivo, filename=nome_arquivo, maintype="application", subtype="octet-stream")

        # Enviar
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(email)
            #print(f"📨 E-mail enviado para {nome_destinatario} <{email_destinatario}>")

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Formulário de contato
# Inicializar variáveis de estado se não existirem
if 'form_nome' not in st.session_state:
    st.session_state.form_nome = ""
if 'form_email' not in st.session_state:
    st.session_state.form_email = ""
if 'form_assunto' not in st.session_state:
    st.session_state.form_assunto = ""
if 'form_mensagem' not in st.session_state:
    st.session_state.form_mensagem = ""

with st.form("contact_form"):
    nome = st.text_input("Nome*", value=st.session_state.form_nome)
    email = st.text_input("Email para contato*", value=st.session_state.form_email)
            
    assunto = st.text_input("Assunto*", value=st.session_state.form_assunto)
    mensagem = st.text_area("Mensagem*", value=st.session_state.form_mensagem)
    anexos = st.file_uploader("Anexos (opcional)", accept_multiple_files=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        submitted = st.form_submit_button("Enviar mensagem", use_container_width=True)
    
    if submitted:
        # Salvar os valores atuais no estado da sessão
        st.session_state.form_nome = nome
        st.session_state.form_email = email
        st.session_state.form_assunto = assunto
        st.session_state.form_mensagem = mensagem
        
        # Validar campos obrigatórios e formato do email
        if not nome or not email or not assunto or not mensagem:
            st.error("Por favor, preencha todos os campos obrigatórios.")
        elif not validar_email(email):
            st.error("Por favor, insira um email válido.")
        else:
            # Converter os arquivos do Streamlit para arquivos temporários
            arquivos_temp = []
            if anexos:
                for arquivo in anexos:
                    # Criar arquivo temporário
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, arquivo.name)
                    
                    with open(temp_path, "wb") as f:
                        f.write(arquivo.getbuffer())
                    arquivos_temp.append(temp_path)

            senha = st.secrets["SENHA_EMAIL"]

            dic_email = {
                "senha": senha,
                "remetente": "vinicius4burame@gmail.com",
                "destinatarios": [{"nome": "", "email": "vinicius4burame@gmail.com"},
                                  {"nome": "", "email": "escamboalado@gmail.com"}],
                "assunto": f"{nome} - {email} - {assunto}",
                "corpo_base": mensagem,
                "anexos": arquivos_temp
            }
            
            try:
                enviar_emails(**dic_email)
                st.success("Obrigado pela mensagem! Entraremos em contato em breve.")
                # Limpar os campos após envio bem-sucedido
                st.session_state.form_nome = ""
                st.session_state.form_email = ""
                st.session_state.form_assunto = ""
                st.session_state.form_mensagem = ""
                
                # Limpar arquivos temporários
                for temp_file in arquivos_temp:
                    try:
                        os.remove(temp_file)
                        os.rmdir(os.path.dirname(temp_file))
                    except:
                        pass
                        
            except Exception as e:
                st.error(f"Erro ao enviar mensagem: {str(e)}")
                
                # Limpar arquivos temporários em caso de erro
                for temp_file in arquivos_temp:
                    try:
                        os.remove(temp_file)
                        os.rmdir(os.path.dirname(temp_file))
                    except:
                        pass

#st.divider()

st.markdown("<p style='text-align: center;'>Desenvolvido por Vinícius Soares e Marla Lorrani para o TRE-BA</p>", unsafe_allow_html=True)