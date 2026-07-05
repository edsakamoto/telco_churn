import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados_csv():
    return pd.read_csv('telco.csv')