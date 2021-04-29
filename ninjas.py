import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import altair as alt
import spacy
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import yfinance as yf
import numpy as np
import base64

# Importar dataset
url_dataset = 'https://github.com/soilmo/GetNinjas/blob/main/get_ninjas.xlsx?raw=true'
@st.cache(show_spinner=False)
def importar_base(url):
    df = pd.read_excel(url, engine='openpyxl')
    return df


# Funções para word cloud -------------------------------------
@st.cache(persist=True, max_entries = 20, ttl = 1800, show_spinner=False)
def stop_lemma(texto, palavras_inuteis):
    nlp = spacy.load('pt_core_news_sm-2.3.0')
    doc = nlp(texto)
    # Tirar Stop Words e Lematização
    filtered_tokens = [token.lemma_ for token in doc if not token.is_stop]
    
    return filtered_tokens

# Define a function to plot word cloud
@st.cache(persist=True, max_entries = 20, ttl = 1800, show_spinner=False)
def plot_cloud(wordcloud):
    # Set figure size
    plt.figure(figsize=(40, 30))
    # Display image
    plt.imshow(wordcloud) 
    # No axis details
    plt.axis("off")

@st.cache(persist=True, max_entries = 20, ttl = 1800, show_spinner=False)
def minusculo(tokens):
    tokens_low = []
    for i in tokens:
        tokens_low.append(i.lower())
    return tokens_low

# Definir tokens e str_word para word cloud
@st.cache(persist=True, max_entries = 20, ttl = 1800, suppress_st_warning=True, show_spinner=False)
def token_and_str_word(df, categoria):

    # Montar tokens
    
    palavras_inuteis = [',',';','a','o','O','as','os','e','para','por','?','!','Não','nao','Nao','não','E','.','-','/',
                    '..','...','<','>','(',')',':','&','$','%','§','pra', ' ','a','b','c','d','e','f','g','h','i','j',
                    'k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','ano','hoje','ontem','yoy','"','mercar',
                    'ficar','ter','entrar','empresar','the','ser','and','to','is','are','on','in','the','it','of','ir','group','ex',
                    '*','"','dar','lixar','ciar','haver','dia','riscar','receitar','“','”','falar','etc','eh','fm','achar',
                    'ja','já','fazer','conseguir','R$','r$','passar','+','-','that','per','mt','with','by','pq','cent',
                    'br','us','hj','dp','ver','contar','estao','mto','=','share','volumar','mm','1x1','sp','en-export',
                    'port','n-export','iv','tesar','rgb','varejar','width','ha','dele','dela','desse','outro','sentir','acontecer',
                    'valorar','trabalham','olhar','unhar','prol','parir','muito','legar']
    my_bar = st.progress(0)
    t = 1
    tokens = []
    erros = 0
    aux = df
    
    for texto in aux[categoria]:
        try:
            tokens = tokens + minusculo(stop_lemma(texto, palavras_inuteis))
        except:
            erros = erros + 1

        evol = t/len(aux[categoria])
        my_bar.progress(evol)
        #st.write("Evolução do processo: {0:1.1f}%".format(100*i/len(aux['texto'])))
        t+=1

    tokens_clean = ['']

    for i in tokens:
        if (i in palavras_inuteis)==False:
            tokens_clean.append(i)
    tokens = tokens_clean

    # Filtrar numeros
    tokens_clean = []
    for i in tokens:
        if i.isnumeric()==False:
            tokens_clean.append(i)
    tokens = tokens_clean
            
    str_word = ''
    for i in tokens:
        str_word = str_word + " " + i
    
    return tokens, str_word
# String to date
def str_to_date(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d')

# Criar link para download
@st.cache(persist=True, max_entries = 20, ttl = 1800, show_spinner=False)
def get_table_download_link(df, arquivo):
    
    csvfile = df.to_csv(index=False)
    b64 = base64.b64encode(csvfile.encode()).decode()
    new_filename = arquivo +".csv"
    href = f'<a href="data:file/csv;base64,{b64}" download="{new_filename}">Download da tabela de frequência de palavras</a>'

    return href

# Title
st.title("Análises Get Ninjas")
# Período de análise
st.header("Período de análise")


# Importar base
df = importar_base(url_dataset)
df = df.sort_values(by=['data'])
st.warning("Data mais antiga: " + str(df['data'].iloc[0]))

dt_i = st.date_input("Qual o dia inicial?", datetime.datetime.now())
dt_i = dt_i.strftime('%Y-%m-%d')

dt_f = st.date_input("Qual o dia final?", datetime.datetime.now())
dt_f = dt_f.strftime('%Y-%m-%d')

# Filtrar
filtro_1 = df['data']>=dt_i
filtro_2 = df['data']<=dt_f
df_dt = df[(filtro_1) & (filtro_2)]

st.success("Base importada. Total de " + str(df_dt.shape[0])+ " avaliações nesse período")

dict_categorias = {
    'Título da Avaliação':'titulo',
    'Prós':'pros',
    'Contras':'contras',
    'Conselhos a Presidência':'conselho'
}

dict_recomenda = {
    'Avaliadores que recomendam':'Recomenda',
    'Avaliadores que não recomendam':'Não recomenda'
}

# Textual
st.header("Análise textual")
# Escolher segmento
categoria = st.selectbox("Qual categoria quer olhar?", options = ['Título da Avaliação','Prós','Contras','Conselhos a Presidência'])
recomenda = st.selectbox("Filtro de recomendação dos avaliadores", options = ['Sem filtro','Avaliadores que recomendam','Avaliadores que não recomendam'])
perspectiva = st.selectbox("Filtro de perspectiva dos avaliadores", options = ['Sem filtro','Perspectiva negativa','Perspectiva neutra','Perspectiva positiva'])

if recomenda != 'Sem filtro' and perspectiva != 'Sem filtro':
    filtro_1 = df_dt['recomenda']==dict_recomenda[recomenda]
    filtro_2 = df_dt['perspectiva']==perspectiva
    df_filtrado = df_dt[filtro_1 & filtro_2]

elif recomenda == 'Sem filtro' and perspectiva != 'Sem filtro':
    filtro = df_dt['perspectiva']==perspectiva
    df_filtrado = df_dt[filtro]

elif recomenda != 'Sem filtro' and perspectiva == 'Sem filtro':
    filtro = df_dt['recomenda']==dict_recomenda[recomenda]
    df_filtrado = df_dt[filtro]

else:
    df_filtrado =df_dt

st.success(str(df_filtrado.shape[0])+ " avaliações após aplicação dos filtros")

if df_filtrado.shape[0]>0:

    if st.checkbox("Montar análises"):

        # Tokens
        tokens, str_word = token_and_str_word(df_filtrado, dict_categorias[categoria])
            
        # Mapa de palavras ---------
        #if st.checkbox("Mapa de palavras"):
        st.markdown("Mapa de palavras")
             
        # Generate word cloud
        wordcloud = WordCloud(width = 700, height = 500, random_state=1, background_color='white', colormap='seismic', collocations=False, stopwords = STOPWORDS).generate(str_word)
        st.image(wordcloud.to_array())

        #if st.checkbox("Frequência de palavras"):
        st.markdown("Frequência de palavras")
        df_freq = pd.DataFrame(list(dict((x,tokens.count(x)) for x in set(tokens)).items()), columns = ['palavra','qtd'])
        df_freq = df_freq.sort_values(by='qtd', ascending=False)
        arquivo = 'freq_palavras_' + categoria
        url_base = get_table_download_link(df_freq, arquivo)
        st.markdown(url_base, unsafe_allow_html=True)
        st.write(df_freq.set_index(['palavra']))
        