import streamlit as st
import pandas as pd

st.set_page_config(page_title='Tabelas - Telco Churn', layout='wide')


usuario = st.session_state.get('usuario','')
if usuario:
    st.markdown(f'**Olá, {usuario} !** ')
    st.markdown(f'Bem vindo à página de Tabelas')

st.title('Tabela de dados')
st.markdown('Explore os dados dos clientes da Telco de forma estática e resumida.')
st.markdown('---')

@st.cache_data
def carregar_dados():
    df = pd.read_csv('telco.csv')
    return df

df = carregar_dados()

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

#indicadores
st.subheader('Indicadores Gerais')

indicador1, indicador2, indicador3, indicador4 = st.columns(4)
total = len(df_filtrado)
churn = df_filtrado[df_filtrado['Churn Label'] == 'Yes'].shape[0]
tempo_medio_permanencia = df_filtrado['Tenure in Months'].mean()
vlr_medio_mensalidade = df_filtrado['Monthly Charge'].mean()

indicador1.metric('Total de Clientes', f'{total:,}')
indicador2.metric('Clientes com Churn',f'{churn:,}',delta=f'{churn / total * 100:.1f}%' if total else '0%')
indicador3.metric('Tempo Médio (meses) até cancelamento',f'{tempo_medio_permanencia:.1f}')
indicador4.metric('Mensalidade Média',f'R$ {vlr_medio_mensalidade:.2f}')

st.markdown('---')

#tabela de dados completa
st.subheader('Dados completos')
colunas_exibir = st.multiselect(
    'Selecione as colunas:',
    options=df_filtrado.columns.tolist(),
    default=['Customer ID','Gender','Age','Contract','Tenure in Months','Monthly Charge'
             ,'Internet Type','Churn Label','Churn Category','Churn Reason']
)
# if colunas_exibir:
#     st.table(df_filtrado[colunas_exibir].head(50))
# else:
#     st.warning('Selecione ao menos uma coluna.')

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