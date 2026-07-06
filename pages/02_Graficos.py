import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
import io
from func.carregar_dados import carregar_dados_csv 

st.set_page_config(page_title='Gráficos - Telco', page_icon=':bar_chart:',layout='wide')

usuario = st.session_state.get('usuario','')
if usuario:
    st.markdown(f'**Olá, {usuario}**')

st.title(':bar_chart: Principais indicadores')
st.markdown('Análise visual dos principais indicadores do dataset Telco.')
st.markdown('---')

#df_churn = df[df['Churn Label'] == 'Yes']

os.makedirs('reports',exist_ok=True)

COLOR_CHURN = '#A33A28'
COLOR_STAY = '#124408' 
COLOR_MAP = {'Yes':COLOR_CHURN, 'No':COLOR_STAY}
REPORTS_DIR = 'reports'
os.makedirs(REPORTS_DIR,exist_ok=True)

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

def save_and_show(fig_ploty,bluid_mpl_fn,filename: str, key:str):
    #exibe a versão interativa (plotly) no dash
    st.plotly_chart(fig_ploty,width='stretch',key=key)

    #constroi versao matplot para exportar
    fig_mpl = bluid_mpl_fn()

    #salva em disco se checkobx 'salvar reports' estiver marcado
    if st.session_state.get('salvar_reports',False):
        path=os.path.join(REPORTS_DIR,filename)
        fig_mpl.savefig(path,bbox_inches='tight',dpi=150)
    
    buf = io.BytesIO()
    fig_mpl.savefig(buf,format='png',bbox_inches='tight',dpi=150)
    buf.seek(0)
    plt.close(fig_mpl)

    st.download_button(
        'Baixar PNG (para email)'
        ,data=buf
        ,file_name=filename
        ,mime='image/png'
        ,key=f'download_{key}'
    )    

df = carregar_dados_csv()
df['Churned'] = df['Churn Label'].map({'Yes':1,'No':0})
df['Faixa Etária'] = pd.cut(
    df['Age'], bins=[0,30,45,60,100]
    ,labels=['<30','30-45','45-60','60+']
)

st.title('Dashboard de Churn - Telco Customer')

st.sidebar.header('Relatório')
st.sidebar.checkbox(
    'Salvar gráficos em reports (para anexar no email)'
    ,key='salvar_reports'
    ,help='Cada gráfico exibido será salvo como PNG na pasta report, pronto para ser anexado em um email'
)
if st.session_state.get('salvar_reports'):
    st.sidebar.caption(f'Salvando em: "./{REPORTS_DIR}/ ')

st.sidebar.header('Filtros')

contract_opts = st.sidebar.multiselect(
    'Tipo de Contrato',options=sorted(df['Contract'].unique())
    ,default=sorted(df['Contract'].unique())
)

internet_opts = st.sidebar.multiselect(
    'Serviço de Internet',options=sorted(df['Internet Service'].unique())
    ,default=sorted(df['Internet Service'].unique())
)

tenure_range = st.sidebar.slider(
    'Tempo de Contrato (meses)'
    ,int(df['Tenure in Months'].min()),int(df['Tenure in Months'].max())
    ,(int(df['Tenure in Months'].min()),int(df['Tenure in Months'].max()))
)

df_f = df[
    df['Contract'].isin(contract_opts) 
    & df['Internet Service'].isin(internet_opts)
    & df['Tenure in Months'].between(*tenure_range)
]

if df_f.empty:
    st.warning('Nenhum registro corresponde aos filtros selecionados.')
    st.stop()

#kpis
col1,col2,col3,col4 = st.columns(4)
col1.metric('Clientes',f'{len(df_f):,}')
col2.metric('Taxa de Churn',f'{df_f['Churned'].mean() * 100:.1f}%')
col3.metric('Ticket Médio Mensal',f'U$ {df_f['Monthly Charge'].mean():.2f}')
col4.metric('CLTV Médio',f'{df_f['CLTV'].mean():,.0f}')

st.divider()

c1,c2 = st.columns(2)

with c1:
    churn_counts = df_f['Churn Label'].value_counts()
    fig_p=px.pie(
        df_f,names='Churn Label', title='Taxa de Churn Geral'
        ,color='Churn Label',color_discrete_map=COLOR_MAP,hole=0.35
    )
    def build_mpl_churn_geral():
        fig,ax = plt.subplots()
        ax.pie(
            churn_counts.values,labels=churn_counts.index,autopct='%1.1f%%'
            ,colors=[COLOR_STAY,COLOR_CHURN],startangle=90
        )
        ax.set_title('Taxa de Churn Geral')
        return fig
    save_and_show(fig_p,build_mpl_churn_geral,'01_taxa_churn_geral.png',key='fig_churn_geral')

with c2:
    contract_churn = (
        df_f.groupby('Contract')['Churned'].mean().mul(100)
        .sort_values(ascending=False).reset_index()
    )
    fig_p = px.bar(
        contract_churn.reset_index(), x='Contract', y='Churned',text='Churned'
        ,title='Taxa de Churn por Tipo de Contrato (%)'
        ,labels={'Churned':'Taxa de Churn(%)'}
        ,color_discrete_sequence=[COLOR_CHURN]
    )
    fig_p.update_traces(texttemplate='%{text:.1f}%',textposition='outside')

    def build_mpl_churn_contrato():
        fig, ax = plt.subplots()
        #bars = ax.bar(contract_churn.index, contract_churn.values, color=COLOR_CHURN)
        bars = ax.bar(
            contract_churn['Contract'], contract_churn['Churned'],color=COLOR_CHURN
        )
        ax.set_ylabel('Taxa de Churn(%)')
        ax.set_title('Taxa de Churn por Tipo de Contrato')
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5, f'{b.get_height():.1f}%',ha='center')
        return fig
    
    save_and_show(fig_p,build_mpl_churn_contrato,'02_churn_por_contrato.png',key='fig_churn_contrato')

c3, c4 = st.columns(2)

with c3:
    fig_p = px.histogram(
        df_f,x='Tenure in Months',color='Churn Label'
        ,barmode='overlay',nbins=30, opacity=0.65
        ,title='Distribuição do tempo de contrato (tenure): Churn x Não Churn'
        ,color_discrete_map=COLOR_MAP
    )

    def build_mpl_tenure():
        fig, ax = plt.subplots()
        ax.hist(df_f.loc[df_f['Churned'] == 0, 'Tenure in Months'],
                 bins=30, alpha=0.6, label='Não Churn', color=COLOR_STAY)
        ax.hist(df_f.loc[df_f['Churned'] == 1, 'Tenure in Months'],
                bins=30,alpha=0.6, label='Churn', color=COLOR_CHURN)
        ax.set_xlabel('Tempo de Relacionamento (meses)')
        ax.set_ylabel('Número de Clientes')
        ax.set_title('Distribuição de Relacionamento com cliente: Churn x Não Churn')
        ax.legend()
        return fig
    
    save_and_show(fig_p,build_mpl_tenure,'03_distrib_tempo_contrato.png',key='fig_rel_cliente')

with c4:
    fig_p = px.box(
        df_f, x='Churn Label', y='Monthly Charge', color='Churn Label'
        ,title='Cobrança Mensal: Churn x Não Churn'
        ,color_discrete_map=COLOR_MAP
    )

    def build_mpl_monthly_charge():
        fig, ax = plt.subplots()
        data_to_plot = [
            df_f.loc[df_f['Churned'] == 0, 'Monthly Charge'],
            df_f.loc[df_f['Churned'] == 1, 'Monthly Charge'],
        ]
        bp = ax.boxplot(data_to_plot, tick_labels=['Não Churn', 'Churn'],patch_artist=True)
        for patch, color in zip(bp['boxes'],[COLOR_STAY,COLOR_CHURN]):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        ax.set_ylabel('Monthly Charge(US$)')
        ax.set_title('Cobrança Mensal: Churn x Não Churn')
        return fig

    save_and_show(fig_p,build_mpl_monthly_charge,'04_cobranca_mensal_boxplot.png',key='fig_cobranca_mensal')

c5,c6 = st.columns(2)

with c5:
    payment_churn = (
        df_f.groupby('Payment Method')['Churned'].mean().mul(100)
        .sort_values(ascending=False).reset_index()
    )
    fig_p = px.bar(
        payment_churn,x='Churned',y='Payment Method',orientation='h'
        ,text='Churned',title='Taxa de Churn por Método de Pagamento(%)'
        ,labels={'Churned': 'Taxa de Churn(%)'}
        ,color_discrete_sequence=[COLOR_CHURN]
    )
    fig_p.update_traces(texttemplate='%{text:.1f}%',textposition='outside')
    fig_p.update_layout(yaxis={'categoryorder':'total ascending'})

    def build_mpl_pagamento():
        fig, ax = plt.subplots()
        #ax.barh(payment_churn.index,payment_churn.values, color=COLOR_CHURN)
        ax.barh(payment_churn['Payment Method'], payment_churn['Churned'],color=COLOR_CHURN)
        ax.set_xlabel('Taxa de Churn(%)')
        ax.set_title('Taxa de Churn por Método de Pagamento')
        ax.invert_yaxis()
        return fig
    
    save_and_show(fig_p,build_mpl_pagamento,'05_churn_por_pagamento.png',key='fig_pagamento')

with c6:
    churn_reason=(
        df_f.loc[df_f['Churned'] == 1, 'Churn Category']
        .value_counts().reset_index()
    )
    fig_p = px.bar(
        churn_reason, x='Churn Category', y='count'
        ,title='Principais Categorias de Motivo de Churn'
        ,color_discrete_sequence=[COLOR_CHURN]
    )

    def build_mpl_motivo():
        fig, ax = plt.subplots()
        #ax.bar(churn_reason.index,churn_reason.values,color=COLOR_CHURN)
        ax.bar(churn_reason['Churn Category'],churn_reason['count'],color=COLOR_CHURN)
        ax.set_ylabel('Número de Clientes')
        ax.set_title('Principais Categorias de Motivo de Churn')
        ax.tick_params(axis='x',rotation=30)
        for label in ax.get_xticklabels():
            label.set_ha('right')
        return fig
    
    save_and_show(fig_p,build_mpl_motivo,'06_categorias_motivo_churn.png',key='fig_motivo')

c7,c8 = st.columns(2)

with c7:
    fig_p = px.histogram(
        df_f,x='Satisfaction Score', color='Churn Label', barnorm='percent'
        ,title='Churn por Nível de Satisfação (%)'
        ,color_discrete_map=COLOR_MAP
    )

    def build_mpl_satisfacao():
        satisfaction_churn = pd.crosstab(
            df_f['Satisfaction Score'], df_f['Churn Label'],normalize='index'
        ) * 100
        fig, ax = plt.subplots()
        satisfaction_churn.plot(kind='bar',stacked=True,ax=ax,color=[COLOR_STAY,COLOR_CHURN])
        ax.set_ylabel('% de Clientes')
        ax.set_xlabel('Satisfaction Score')
        ax.set_title('Churn por Nível de Satisfação')
        ax.legend(title='Churn')
        return fig
    
    save_and_show(fig_p,build_mpl_satisfacao,'07_satisfacao_churn.png',key='fig_satisfacao')

with c8:
    age_churn = (
        df_f.groupby('Faixa Etária')['Churned'].mean().mul(100).reset_index()
    )
    fig_p = px.bar(
        age_churn, x='Faixa Etária', y='Churned'
        ,title='Taxa de Churn por Faixa Etária (%)'
        ,labels={'Churned':'Taxa de Churn (%)'}
        ,color_discrete_sequence=[COLOR_CHURN]
    )

    def build_mpl_faixa_etaria():
        fig, ax = plt.subplots()
        #ax.bar(age_churn.index.astype(str),age_churn.values, color=COLOR_CHURN)
        ax.bar(age_churn['Faixa Etária'],age_churn['Churned'],color=COLOR_CHURN)
        ax.set_ylabel('Taxa de Churn(%)')
        ax.set_xlabel('Faixa Etária')
        ax.set_title('Taxa de Churn por Faixa etária')
        return fig
    
    save_and_show(fig_p,build_mpl_faixa_etaria,'08_churn_por_faixa_etaria.png',key='fig_faixa_etaria')

#Scatter de life time value x churn score

fig_p = px.scatter(
    df_f,x='Churn Score', y='CLTV', color='Churn Label'
    ,size='Monthly Charge',hover_data=['Customer ID','Contract','Tenure in Months']
    ,title='CLTV x Churn Score (tamanho = Cobrança Mensal)'
    ,color_discrete_map=COLOR_MAP,opacity=0.6
)

def build_mpl_cltv():
    fig, ax = plt.subplots(figsize=(10,5))
    for label, color in [('No', COLOR_STAY), ('Yes',COLOR_CHURN)]:
        subset = df_f[df_f['Churn Label'] == label]
        ax.scatter(subset['Churn Score'],subset['CLTV']
                   ,s=subset['Monthly Charge'] / 3, alpha=0.4, color=color, label=label)
    ax.set_xlabel('Churn Score')
    ax.set_ylabel('CLTV')
    ax.set_title('CLTV x Churn Score (tamanho = Cobrança Mensal)')
    ax.legend(title='Churn')

    return fig

save_and_show(fig_p,build_mpl_cltv,'09_cltv_x_churn_score.png',key='fig_cltv')

with st.expander('Ver dados filtrados(tabela)'):
    st.dataframe(df_f)


# #pizza
# st.subheader('Taxa de Churn')
# qtd_churn = df['Churn Label'].value_counts().reset_index()
# qtd_churn.columns = ['Status', 'Quantidade']
# fig1 = px.pie(
#     qtd_churn,values='Quantidade',names='Status'
#     ,color_discrete_sequence=["#124408", "#A33A28"]
#     ,title='% de Clientes que Cancelaram '
#     ,hole=0.4
# )

# st.plotly_chart(fig1,width='stretch')

# #salvar para o email
# fig_m, ax = plt.subplots()
# ax.pie(
#     qtd_churn['Quantidade'],labels=qtd_churn['Status']
#     ,autopct='%1.1f%%', colors=["#124408", "#A33A28"]
# )
# ax.set_title('Taxa de Churn')
# fig_m.savefig('reports/churn_geral.png',bbox_inches='tight')
# plt.close(fig_m)
# st.markdown('---')