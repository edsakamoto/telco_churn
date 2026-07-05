import streamlit as st
import pandas as pd
from func.carregar_dados import carregar_dados_csv 

st.set_page_config(page_title='Tabelas - Telco Churn', layout='wide')


usuario = st.session_state.get('usuario','')
if usuario:
    st.markdown(f'**Olá, {usuario} !** ')
    st.markdown(f'Bem vindo à página de Tabelas')

st.title('Tabela de dados')
st.markdown('Explore os dados dos clientes da Telco de forma estática e resumida.')
st.markdown('---')

df = carregar_dados_csv()

#Filtros
st.subheader('Filtros')
col1,col2,col3 = st.columns(3)
with col1:
    filtro_churn = st.selectbox('Status de Churn:', ['Todos','Sim','Não'])
with col2:
    filtro_contrato = st.multiselect(
        'Tipo de Contrato:',
        options=df['Contract'].dropna().unique().tolist(),
        default=df['Contract'].dropna().unique().tolist()
    )
with col3:
    filtro_internet = st.multiselect(
        'Tipo de Internet:',
        options=df['Internet Type'].dropna().unique().tolist(),
        default=df['Internet Type'].dropna().unique().tolist()
    )

df_filtrado = df.copy()

if filtro_churn != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Churn Label'] == filtro_churn]
if filtro_contrato:
    df_filtrado = df_filtrado[df_filtrado['Contract'].isin(filtro_contrato)]
if filtro_internet:
    df_filtrado = df_filtrado[df_filtrado['Internet Type'].isin(filtro_internet)]

st.markdown('---')

#tabela de dados completa
st.subheader('Dados completos')
colunas_exibir = st.multiselect(
    'Selecione as colunas:',
    options=df_filtrado.columns.tolist(),
    default=['Customer ID','Gender','Age','Contract','Tenure in Months','Monthly Charge'
             ,'Internet Type','Churn Label','Churn Category','Churn Reason']
)

# st.caption(f'Exibindo até 50 de {total} registros filtrados.')
if colunas_exibir:
    st.dataframe(
        df_filtrado[colunas_exibir]
        ,height=500
        ,width='stretch'
    )
else:
    st.warning('Selecione ao menos uma coluna')
st.caption(f'Total de {len(df_filtrado)} registros filtrados (use scroll para navegar).')

st.markdown('---')

#Distribuição de churn por categoria
st.subheader('Churn x Categoria')
churn_cat = (
    df_filtrado[df_filtrado['Churn Label'] == 'Yes']
    .groupby('Churn Category')
    .size()
    .reset_index(name='Quantidade')
    .sort_values('Quantidade',ascending=False)
)

st.dataframe(churn_cat,hide_index=True)

#top motivos de churn
st.subheader('Top 10 Motivos de Churn')
top_motivos = (
    df_filtrado[df_filtrado['Churn Label'] == 'Yes']
    .groupby('Churn Reason')
    .size()
    .reset_index(name='Quantidade')
    .sort_values('Quantidade',ascending=False)
    .head(10)
)

st.dataframe(top_motivos,hide_index=True)