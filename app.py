import streamlit as st

st.set_page_config(
    page_title='Trabalho pós'
    ,page_icon=':robot:'
    ,layout='wide'
)

st.sidebar.title("Navegação")
nome = st.sidebar.text_input("Seu nome:",placeholder="Digite seu nome aqui")
if nome:
    st.session_state['usuario'] = nome
elif 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""

st.sidebar.markdown('---')
st.sidebar.info('Use o menu acima para navegar entre as páginas')

st.title('Dashboard')
st.markdown('### Análise de churn da Telco')

if st.session_state.get('usuario'):
    st.success(f'Olá, **{st.session_state['usuario']}**! Que bom ter você por aqui')

st.markdown('---')

col1 , col2, col3 = st.columns(3)
with col1:
    st.markdown('#### Tabelas')
    str.write('Explore os dados brutos e estatísticas resumidas dos clientes da Telco')
with col2:
    st.markdown('#### Gráficos')
    st.write('Visualize os principais indicadores de churn de forma interativa')
with col3:
    st.markdown('#### Envio de E-mail')
    st.write('Envie insights e gráficos diretamente para sua caixa de entrada!')

st.markdown('---')
st.markdown('#### Sobre o projeto')

st.write(
    '''
    Dashboard desenvolvido para trabalho de pós graduação da YTO Academy pela matéria "DataViz com Python".
    Possuindo como objetivo analisar um dataset em csv para identificar padrões de cancelamento, compreender 
    os motivos que levam os clientes a deixar a empresa e gerar insights acionáveis para reduzir a taxa de churn

    ** Dataset: ** IBM Telco Customer Churn
    ** Total de clientes: ** 7.043
    ** Colunas analisadas: ** 50 atributos por cliente

    '''
)

st.markdown('---')
st.caption('Projeto de estudos - Matéria: DataViz com Python - YTO Academy')