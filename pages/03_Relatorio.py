import os
import io
import pandas as pd
from datetime import datetime
import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from func.carregar_dados import carregar_dados_csv

st.set_page_config(page_title='Envio de email - Relatório da Telco',page_icon=':email:', layout='wide')

usuario = st.session_state.get('usuario','')
if usuario:
    st.markdown(f'**Olá, {usuario}** :wave:')

st.title(':email: Relatório de Churn')
st.markdown(
    'O relatório gerado de forma dinâmico'
    'Você pode fazer o **download** em `.txt` ou **enviar por email** '
    '(com os gráficos da página Gráficos anexados)'
)

st.markdown('---')

df = carregar_dados_csv()
df_churn = df[df['Churn Label'] == 'Yes']
df_ativo = df[df['Churn Label'] == 'No']

def gerar_relatorio(nome_usuario: str) -> str:
    agora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    total = len(df)
    n_churn = len(df_churn)
    n_ativo = len(df_ativo)
    taxa = n_churn / total * 100

    avg_tenure_churn = df_churn['Tenure in Months'].mean()
    avg_tenure_ativo = df_ativo['Tenure in Months'].mean()
    avg_charge_churn = df_churn['Monthly Charge'].mean()
    avg_charge_ativo = df_ativo['Monthly Charge'].mean()

    top_categorias = df_churn['Churn Category'].value_counts().head()
    top_motivos = df_churn['Churn Reason'].value_counts().head(10)
    por_contrato = (
        df.groupby(['Contract','Churn Label']).size().unstack(fill_value=0)
    )
    por_internet = (
        df.groupby(['Internet Type','Churn Label']).size().unstack(fill_value=0)
    )
    sat_churn = df_churn['Satisfaction Score'].mean()
    sat_ativo = df_ativo['Satisfaction Score'].mean()

    linhas = [

        '=' * 70,
        '  TELCO CHURN DASHBOARD - RELATÓRIO ANALÍTICO COMPLETO  ',
        '=' * 70,
        f' Gerado por   : {nome_usuario if nome_usuario else 'Usuário'} ',
        f' Data/Hora    : {agora} ',
        f' Dataset      : IBM Telco Customer Churn ',
        '=' * 70,
        '',
        '1. Visão Geral',
        '-' * 50,        
        f' Total de clientes         : {total:,}   ',
        f' Clientes com Churn(Sim)   : {n_churn:,} ',
        f' Clientes Ativos (Não)     : {n_ativo:,} ',
        f' Taxa de Churn             : {taxa:.2f}% ',
        '',
        '2. Tempo de Contrato (Tenure)',
        '-' * 50,
        f' Tempo médio - Com Churn   : {avg_tenure_churn:.1f} meses ',
        f' Tempo médio - Sem Churn   : {avg_tenure_ativo:.1f} meses ',
        f' Insight: Clientes que cancelaram ficaram em média {avg_tenure_ativo - avg_tenure_churn:.1f} meses a menos do que os clientes ativos.',        
        '',
        '3. Cobrança Mensal',
        '-' * 50,
        f' Valor Médio da Mensal - Com Churn   : US$ {avg_charge_churn:.2f} ',
        f' Valor Médio da Mensal - Sem Churn   : US$ {avg_charge_ativo:.2f} ',
        f' Diferença                           : US$ {avg_charge_churn - avg_charge_ativo:.2f} ',
        f' Insight: Clientes com churn pagavam em média {((avg_charge_churn/avg_charge_ativo)-1)*100:.1f}% a mais por mês em comparação aos que permaneceram.',        
        '',
        '4. Score de Satisfação',
        '-' * 50,
        f' Score Médio - Com Churn   : {sat_churn:.2f} / 5 ',
        f' Score Médio - Sem Churn   : {sat_ativo:.2f} / 5 ',
        '',
        '5. Top 5 categorias de Churn',
        '-' * 50
    ]

    for cat, qtd in top_categorias.items():
        pct = qtd / n_churn * 100
        linhas.append(f'  {cat:<35}: {qtd:>4} ({pct:.1f}%)')
    
    linhas += ['','6. Top 10 Motivos de Churn', '-' * 50]
    for motivo, qtd in top_motivos.items():
        pct = qtd / n_churn * 100
        linhas.append(f'  {motivo:<45}: {qtd:>4} ({pct:.1f}%)')
    
    linhas +=['','7. Churn por Tipo de Contrato', '-' * 50]
    for contrato in por_contrato.index:
        yes = por_contrato.loc[contrato, 'Yes'] if 'Yes' in por_contrato.columns else 0
        no = por_contrato.loc[contrato, 'No'] if 'No' in por_contrato.columns else 0
        total_c = yes + no
        pct_c = yes / total_c * 100 if total_c else 0
        linhas.append(f'  {contrato:<25}: {yes:>4} churns / {total_c:>4} total ({pct_c:.1f}%)')
    
    linhas +=['','8. Churn por Tipo de Internet','-' * 50]
    for internet in por_internet.index:
        yes = por_internet.loc[internet, 'Yes'] if 'Yes' in por_internet.columns else 0
        no = por_internet.loc[internet, 'No'] if 'No' in por_internet.columns else 0
        total_i = yes + no
        pct_i = yes / total_i * 100 if total_i else 0
        linhas.append(f'  {internet:<25}: {yes:>4} churns / {total_i:>4} total ({pct_i:.1f}%)')
    
    linhas += [
        '',
        '9. Recomendações estratégicas',
        '-' * 50,
        '  [1] Criar programas de rentação nos primeiros 12 meses de contrato.',
        '  [2] Incentivar migração de contratos mensais para anuais / bianuais.',
        '  [3] Revisar precificação para clientes com cobrança mensal acima.',
        '      da média (oferecer descontos de fidelidade).'
        '  [4] Implementar pesquisas de satisfação proativas (NPS Mensal).',
        '  [5] Desenvolver estratégia competitiva para responder a ofertas.',
        '      de concorrentes (principal motivo de churn).',
        '  [6] Melhorar o atendimento ao cliente (Attitude é a 2ª causa).',
        '',
        '=' * 70,
        '  Relatório gerado automaticamente pelo App Churn Dashboard',
        '=' * 70
    ]

    return '\n'.join(linhas)

#inicializa o relatório automatico
relatorio = gerar_relatorio(usuario)

st.session_state['relatorio_txt'] = relatorio #armazena no session para não recalcular a cada iteracao

st.subheader('Preview do Relatório')
with st.expander('Ver relatório completo',expanded=True):
    st.text(relatorio)

st.markdown('---')

#escolher download ou enviar email
tab_download, tab_email = st.tabs([':arrow_down: Baixar Relatório', ':email: Enviar por email'])

#download
with tab_download:
    st.subheader('Download do Relatório(.txt)')
    col1,col2 = st.columns([1,2])
    with col1:
        nome_arquivo = st.text_input(
            'Nome do arquivo:',value=f'relatorio_churn_telco_{datetime.now().strftime('%d_%m_%Y')}.txt',key='nome_arquivo_download'
        )
    with col2:
        st.write('')
        st.write('')
        buffer = io.BytesIO(relatorio.encode('utf-8'))
        st.download_button(
            label='Baixar Realtório(.txt)'
            ,data=buffer
            ,file_name=nome_arquivo
            ,mime='text/plain'
            ,type='primary'
        )

#email
with tab_email:
    st.subheader('Enviar relatório por email')
    st.markdown(
        'O relatório completo é anexado automaticamente como arquivo .txt. '
        'É possível anexar os gráficos gerados da página **Gráficos** (necessário ter acessado a página ao menos uma vez durante a sesssão)'
    )

    #necessario configurar arquivos de segredos dentro do streamlit
    remetente = st.secrets.get('EMAIL',None)
    senha = st.secrets.get('PASS',None)

    if not remetente or not senha:
        st.error(
            'Credenciais de e-mail não configuradas. Adicione email e senha no arquivo secrets dentro do streamlit'
        )
    
    st.caption(f'Remetente configurado: **{remetente or '-'}** ')

    with st.form('form_email_relatorio'):
        col1, col2 = st.columns(2)
        with col1:
            destinatario = st.text_input('E-mail destinatário:', placeholder='destinatario@email.com')
        with col2:
            assunto = st.text_input('Assunto:', value='Relatório de Churn - Telco Dashboard')
        
        mensagem = st.text_area(
            "Mensagem do e-mail:"
            ,value=(
                'Olá,\n\n'
                'Segue anexo relatório completo de análise de churn '
                'gerado pela página, além dos gráficos correspondentes'
                '(quando selecionados abaixo). \n\n'
                'Um resumo do relatório também está disponível no corpo deste email'
            )
            ,height=159
        )

        nome_anexo_relatorio = st.text_input(
            'Nome do anexo do relatório:', value=f'relatorio_churn_telco_{datetime.now().strftime('%d_%m_%Y')}.txt'
        )
        
        st.markdown('**Anexar gráficos** (gerados na página Gráficos)')
        graficos_disponiveis = {
            'Taxa de Churn Geral'            : 'reports/01_taxa_churn_geral.png'
            ,'Churn por Contrato'            : 'reports/02_churn_por_contrato.png'
            ,'Churn por Tempo de Contrato'   : 'reports/03_distrib_tempo_contrato.png'
            ,'Churn por Cobrança Mensal'     : 'reports/04_cobranca_mensal_boxplot.png'
            ,'Churn por Tipo de Pagamento'   : 'reports/05_churn_por_pagamento.png'
            ,'Churn por Categorias de motivo': 'reports/06_categorias_motivo_churn.png'
            ,'Churn por Satisfação'          : 'reports/07_satisfacao_churn.png'
            ,'Churn por Faixa etária'        : 'reports/08_churn_por_faixa_etaria.png'
            ,'Gráf. de dist. por CLTV e Score de Churn': 'reports/09_cltv_x_churn_score.png'
        }
        graficos_selecionados = []
        for nome_grafico, caminho in graficos_disponiveis.items():
            if os.path.exists(caminho):
                if st.checkbox(f'{nome_grafico}', value=True, key=f'chk_{nome_grafico}'):
                    graficos_selecionados.append((nome_grafico,caminho))
            else:
                st.warning(
                    f' "{nome_grafico}" não encontrado. Acesse a página **Gráficos** primeiro para gerá-lo'
                )
        
        enviar = st.form_submit_button('Enviar Email', type='primary')
    
    if enviar:
        if not remetente or not senha:
            st.error(
                'Credenciais de email não configurados no servidor do streamlit'
            )
        elif not destinatario:
            st.error('Por favor, informe o email destinatário')
        else:
            with st.spinner('Enviando email...'):
                try:
                    msg = MIMEMultipart('mixed')
                    msg['From'] = remetente
                    msg['To'] = destinatario
                    msg['Subject'] = assunto

                    corpo = MIMEMultipart('related')

                    html_body = f'''
                    <html><body>
                    <h2>Relatório de Churn - Telco Dashboard</h2>
                    <p style='font-family:sans-serif; font-size:14px;'>{mensagem.replace(chr(10),'<br>')}</p>
                    <hr>
                    '''
                    for i,(nome_g, _) in enumerate(graficos_selecionados):
                        html_body += f'<h3>{nome_g}</h3><img src="cid:grafico{i}"><br><br>'
                    html_body += (
                        '<p><em>Relatório completo em anexo(.txt) '
                        'Enviando através do App Churn Dashboard.</em></p>'
                        '</body></html>'
                    )

                    corpo.attach(MIMEText(html_body,'html'))

                    for i, (nome_g,caminho) in enumerate(graficos_selecionados):
                        with open(caminho,'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<grafico{i}>')
                            img.add_header(
                                'Content-Disposition', 'inline'
                                ,filename=os.path.basename(caminho)
                            )
                            corpo.attach(img)
                    msg.attach(corpo)

                    anexo_relatorio = MIMEApplication(
                        relatorio.encode('utf-8'), _subtype='plain'
                    )
                    anexo_relatorio.add_header(
                        'Content-Disposition','attachment',filename=nome_anexo_relatorio
                    )
                    msg.attach(anexo_relatorio)

                    for nome_g, caminho in graficos_selecionados:
                        with open(caminho,'rb') as f:
                            anexo_img = MIMEApplication(f.read(),_subtype='png')
                            anexo_img.add_header(
                                'Content-Disposition','attachment'
                                ,filename=os.path.basename(caminho)
                            )
                            msg.attach(anexo_img)
                    
                    with smtplib.SMTP_SSL('smtp.gmail.com',465) as servidor:
                        servidor.login(remetente,senha)
                        servidor.sendmail(remetente,destinatario,msg.as_string())
                    
                    st.success(f'Email enviado com sucesso para **{destinatario}**!')
                    st.balloons()

                except smtplib.SMTPAuthenticationError:
                    st.error(
                        'Falha na autenticação. Verifique os valores de EMAIL e PASS configurados no servidor'
                    )
                except Exception as e:
                    st.error(f'Erro ao enviar: {e}')
    
    st.markdown('---')


st.caption('O relatório é gerado dinamicamente com base nos dados carregados do arquivo telco.csv do servidor.')
            



