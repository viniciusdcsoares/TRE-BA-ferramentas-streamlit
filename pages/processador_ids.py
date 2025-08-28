import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# -----------------------------------------------------------------------------
# CONSTANTES E CONFIGURAÇÕES INICIAIS
# -----------------------------------------------------------------------------

# Título da página e ícone
st.set_page_config(page_title="Processador de IDS", page_icon="🌴")
st.title("🌴 Processador de Indicadores de Desempenho de Sustentabilidade (IDS)")
st.markdown("""
Esta ferramenta automatiza a geração de relatórios de sustentabilidade a partir de uma planilha de dados.
Siga os passos abaixo para obter seu arquivo Excel com os valores absolutos e os indicadores relativos calculados.
""")
st.divider()

# Dados que não mudam (constantes do script original)
TRIBUNAIS_PARA_MANTER = [
    "TRE", "TRE-AC", "TRE-AL", "TRE-AM", "TRE-AP", "TRE-BA", "TRE-CE",
    "TRE-DF", "TRE-ES", "TRE-GO", "TRE-MA", "TRE-MG", "TRE-MS", "TRE-MT",
    "TRE-PA", "TRE-PB", "TRE-PE", "TRE-PI", "TRE-PR", "TRE-RJ", "TRE-RN",
    "TRE-RO", "TRE-RR", "TRE-RS", "TRE-SC", "TRE-SE", "TRE-SP", "TRE-TO"
]

MAPA_NOMES_ABSOLUTOS = {
    "tribunal": "Tribunal", "cee": "Consumo de energia eletrica (kWh)", "ca": "Consumo de agua (m2)",
    "qve": "Quantidade total de veiculos", "cc": "Consumo de copos descartaveis", "gc": "Gasto com combustivel",
    "gmv": "Gasto com manutencao de veiculos", "gcm": "Gastos com contratos de motoristas",
    "gcv": "Gasto com contratos de agenciamento de transporte terrestre", "got": "Gasto com outros tipos de transportes",
    "gpp": "Gasto com papel proprio", "gcgraf": "Gastos com servicos graficos no periodo-base",
    "tmr": "Total de materiais destinados a reciclagem", "gaed": "Gasto com agua mineral em embalagens descartaveis",
    "gtf": "Gasto com telefonia fixa", "gtm": "Gasto com telefonia movel", "qei": "Quantidade de equipamentos de impressao",
    "Pservcf": "Percentual de servidoras ocupantes de cargo de chefia", "ftt": "Forca de trabalho total",
    "mtotal": "Area total em metros quadrados"
}

# -----------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# -----------------------------------------------------------------------------
def processar_dados(arquivo_csv, ano_referencia):
    """
    Função que encapsula toda a lógica de processamento dos dados.
    Recebe o arquivo carregado e o ano, retorna os dois dataframes (absoluto e relativo).
    """
    try:
        ano_referencia_str = str(ano_referencia)

        # --- 1. LEITURA E FILTRO INICIAL ---
        # Lê o arquivo CSV diretamente do objeto carregado pelo Streamlit
        base = pd.read_csv(arquivo_csv, sep=';', encoding='latin1', low_memory=False, dtype=str)
        
        base_filtrada = base[(base['periodicidade'] == "Anual") & (base['ano'] == ano_referencia_str)].copy()
        base_filtrada = base_filtrada[base_filtrada['tribunal'].isin(TRIBUNAIS_PARA_MANTER)].copy()

        if base_filtrada.empty:
            st.warning(f"Nenhum dado encontrado para o ano {ano_referencia_str} com os filtros aplicados.")
            return None, None

        # --- 2. PREPARAÇÃO DOS DADOS ABSOLUTOS (COMO TEXTO) ---
        colunas_abs = list(MAPA_NOMES_ABSOLUTOS.keys())
        colunas_abs_existentes = [col for col in colunas_abs if col in base_filtrada.columns]
        relatorio_absoluto = base_filtrada[colunas_abs_existentes].copy()
        relatorio_absoluto.rename(columns=MAPA_NOMES_ABSOLUTOS, inplace=True)

        # --- 3. PREPARAÇÃO DOS DADOS PARA CÁLCULO (CONVERSÃO NUMÉRICA) ---
        base_numerica = base_filtrada.copy()
        colunas_para_converter = list(MAPA_NOMES_ABSOLUTOS.keys())
        for coluna in colunas_para_converter:
            if coluna in base_numerica.columns and coluna != 'tribunal':
                # Limpa e converte a coluna para formato numérico
                texto = base_numerica[coluna].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                base_numerica[coluna] = pd.to_numeric(texto, errors='coerce')

        # --- 4. CÁLCULO DOS INDICADORES RELATIVOS ---
        relatorio_relativo = pd.DataFrame()
        relatorio_relativo['Tribunal'] = base_numerica['tribunal']

        def divide_seguro(numerador, denominador):
            # Garante que a divisão por zero ou por NaN retorne 0
            return np.where(denominador.fillna(0) > 0, numerador.fillna(0) / denominador, 0)

        # Dicionário de fórmulas para os indicadores
        formulas = {
            'Consumo de energia elétrica (kWh) per capita': ('cee', 'ftt'),
            'Consumo de energia elétrica (kWh) por metro quadrado': ('cee', 'mtotal'),
            'Consumo de água (m3) per capita': ('ca', 'ftt'),
            'Consumo de água (m3) por metro quadrado': ('ca', 'mtotal'),
            'Número de usuários (as) por veículo': ('ftt', 'qve'),
            'Consumo de copos descartáveis per capita': ('cc', 'ftt'),
            'Gastos de transporte per capita': (base_numerica[['gc', 'gmv', 'gcm', 'gcv', 'got']].sum(axis=1), base_numerica['ftt']),
            'Gastos de papel per capita': (base_numerica[['gpp', 'gcgraf']].sum(axis=1), base_numerica['ftt']),
            'Destinação de material para reciclagem em relação à força de trabalho total': ('tmr', 'ftt'),
            'Consumo de água envasada descartável per capita': ('gaed', 'ftt'),
            'Gastos de telefonia per capita': (base_numerica[['gtf', 'gtm']].sum(axis=1), base_numerica['ftt']),
            'Quantidade de equipamentos de impressão per capita': ('qei', 'ftt')
        }

        for nome_indicador, (numerador_key, denominador_key) in formulas.items():
            numerador = base_numerica[numerador_key] if isinstance(numerador_key, str) else numerador_key
            denominador = base_numerica[denominador_key] if isinstance(denominador_key, str) else denominador_key
            relatorio_relativo[nome_indicador] = divide_seguro(numerador, denominador)

        return relatorio_absoluto, relatorio_relativo

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante o processamento: {e}")
        st.exception(e) # Mostra o traceback completo para depuração
        return None, None

# -----------------------------------------------------------------------------
# INTERFACE DO USUÁRIO (COMPONENTES STREAMLIT)
# -----------------------------------------------------------------------------

# 1. Uploader de arquivo
uploaded_file = st.file_uploader(
    "**Passo 1: Selecione a planilha de dados**",
    type="csv",
    help="O arquivo deve ser no formato .csv e separado por ponto e vírgula (;)"
)

# 2. Input do ano
ano_atual = datetime.now().year
ano_referencia = st.number_input(
    "**Passo 2: Informe o Ano de Referência**",
    min_value=2000,
    max_value=ano_atual + 1,
    value=ano_atual,
    step=1,
    help=f"Selecione o ano dos dados que deseja processar. O padrão é {ano_atual}."
)

st.divider()

# 3. Botão para iniciar o processamento
if st.button("🚀 Gerar Relatórios", type="primary", use_container_width=True):
    if uploaded_file is not None:
        with st.spinner('Aguarde, processando os dados... Isso pode levar alguns segundos.'):
            # Chama a função de processamento
            df_abs, df_rel = processar_dados(uploaded_file, ano_referencia)

        # Se o processamento foi bem-sucedido, mostra os resultados e o botão de download
        if df_abs is not None and df_rel is not None:
            st.success("✅ Processamento concluído com sucesso!")

            # Prepara o arquivo Excel em memória para download
            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                df_abs.to_excel(writer, sheet_name='Valores Absolutos', index=False)
                df_rel.to_excel(writer, sheet_name='Indicadores Relativos', index=False)
            
            output_buffer.seek(0) # Volta ao início do buffer para a leitura

            # Cria o botão de download
            st.download_button(
                label="📥 Baixar Relatório em Excel",
                data=output_buffer,
                file_name=f"Relatorios_Sustentabilidade_{ano_referencia}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            # Exibe prévias dos dados na tela usando abas
            st.markdown("### Pré-visualização dos Relatórios Gerados")
            tab1, tab2 = st.tabs(["Valores Absolutos", "Indicadores Relativos"])
            with tab1:
                st.dataframe(df_abs)
            with tab2:
                st.dataframe(df_rel)

    else:
        # Mensagem de erro se nenhum arquivo foi selecionado
        st.error("❌ Por favor, selecione um arquivo .csv primeiro.")