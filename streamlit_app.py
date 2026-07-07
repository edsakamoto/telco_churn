import streamlit as st

st.set_page_config(
    page_title='Inicializador'
    ,page_icon=':robot:'
    ,layout='wide'
)

pg = st.navigation(
    [
        st.Page('./pages/00_Home.py',title='Página Inicial')
        ,st.Page('./pages/01_Tabelas.py',title='Tabelas')
        ,st.Page('./pages/02_Graficos.py',title='Gráficos')
        ,st.Page('./pages/03_Relatorio.py',title='Relatório e Envio de Email')        
    ]
)

pg.run()