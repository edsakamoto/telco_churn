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