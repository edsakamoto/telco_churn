# Projeto para aula de Pós da YTO Academy - Materia DataViz com Python

Dashboard interativo de análise de churn desenvolvido com **streamlit** e **python 3.12**

## Estrutura do projeto
```
Home.py #Página inicial (home)
telco.csv # Dataset IBM Telco Customer Churn
requirement.txt #Dependencias
.gitignore
pages/
    - 01_Tabelas.py #Tabelas estáticas
    - 02_Graficos.py #Visualizações interativas
    - 03_Relatorio.py #Envio de email e download do relatório
reports/ #graficos em PNG gerado automaticamente
func/ #funções gerais
```

## Como executar localmente

```
bash
#1. Crie e ative o ambiente virtual
python -m venv venv
venv/Scripts/Activate

#2. Instale as dependencias
pip install --upgrade pip
pip install -r requirements.txt

#3. Execute o aplicativo
streamlit run Home.py
```

## Páginas

| Página | Descrição |
|--------|-----------|
| **Home** | Apresentação do dashboard e captura o nome do usuário |
| **Tabelas** | Dados filtráveis, resumo estatístico |
| **Gráficos** | Visualizações interativas sobre churn |
| **Relatório** | Possibilidade de download(.txt) e enviar por email relatório e gráficos |