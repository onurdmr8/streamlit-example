import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
from sqlalchemy import text
import subprocess

genelbg = '#ECE5C7'

st.set_page_config(layout="wide")
st.title('666')
st.markdown('<style>body{background-color: %s;}</style>' % genelbg, unsafe_allow_html=True)

@st.cache_data
def get_data():
    ServerName = "VSTRAPP"
    MSQLDatabase = "VSA2023"
    username = "DescomKasa"
    password = "D123456d*"
    connection_string = "DRIVER={SQL Server};SERVER=" + ServerName + ";DATABASE=" + MSQLDatabase + ";UID=" + username + ";PWD=" + password + ";charset=utf-8"
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
    query = "SELECT ISEMRINO, TARIH, STOK_KODU, MIKTAR, TESLIM_TARIHI, SIPARIS_NO, KAPALI FROM TBLISEMRI"
    df = pd.read_sql(query, engine)
    stok_query = "SELECT STOK_KODU, STOK_ADI FROM TBLSTSABIT"
    stok_df = pd.read_sql(stok_query, engine)
    # Merge the two dataframes on 'STOK_KODU'
    df = df.merge(stok_df, on='STOK_KODU', how='left')
    df2 = df[['ISEMRINO', 'TARIH', 'STOK_KODU', 'STOK_ADI', 'MIKTAR', 'TESLIM_TARIHI', 'SIPARIS_NO', 'KAPALI']]
    return df2

data = get_data()

def colorize_rows(row):
    if row['KAPALI'] == "E":
        return ['background-color: #000000'] * 8
    else:
        return ['background-color: #210062'] * 8
def filter_data(df, tarih, surec):
    filtered_df = df.copy()
    tarih = tarih.strftime("%d-%m-%Y")
    filtered_df = filtered_df[filtered_df['TARIH'] == tarih]
    if surec != "hepsi":
        if surec == "seçme":
            surex = "03"
        elif surec == "fırın":
            surex = "05"
        elif surec == "IQF":
            surex = "06"
        elif surec == "kalite":
            surex = "01"
        elif surec == "paketleme":
            surex = "07"
        elif surec == "kantar":
            surex = "01"
        elif surec == "meyve kesme":
            surex = "04"
        elif surec == "reçel":
            surex = "08"
        elif surec == "püre":
            surex = "09"
        elif surec == "yarı mamul":
            surex = "10"
        filtered_df = filtered_df[filtered_df['ISEMRINO'].str.startswith(surex)]
    else:
        filtered_df = df.copy()
    if vardiya != "hepsi":
        if vardiya=="00:00-08:00":
            vardiyax="1"
        elif vardiya=="08:00-16:00":
            vardiyax="2"
        elif vardiya=="16:00-24:00":
            vardiyax="3"
        filtered_df = filtered_df[filtered_df['ISEMRINO'].str[2] == vardiyax]
    return filtered_df

container = st.container()
container2=st.container()
container2.markdown('<style>div[data-baseweb="select"] { width: 300px !important; }</style>', unsafe_allow_html=True)
columns = st.columns(2)
with columns[0]:
    tarih = st.date_input('Tarih seçin:')
    surec = st.selectbox('İş Emri Süreci seçin:',
                         ['hepsi', 'seçme', 'fırın', 'IQF', 'kalite', "paketleme", "kantar", "meyve kesme", "reçel",
                          "püre", "yarı mamul"])
    vardiya = st.selectbox('Vardiya seçin:', ['hepsi', '00:00-08:00', '08:00-16:00', '16:00-24:00'])
    filtered_data = filter_data(data, tarih, surec)
    container.markdown('<style>div[data-baseweb="select"] { width: 300px !important; }</style>',
                       unsafe_allow_html=True)
    container.markdown('<style>div[data-baseweb="input"] { width: 300px !important; }</style>',
                       unsafe_allow_html=True)
with columns[1]:

    yeni_deger = st.selectbox('kapali mi?', ['E', 'H'])
    emir_no = st.text_input('İş Emri No:')
    st.write("")
    st.write("")
    update = st.button('Güncelle')
st.dataframe(filtered_data.style.apply(colorize_rows, axis=1), use_container_width=True)

def update_kapali_value(emir_no, yeni_deger):
    ServerName = "VSTRAPP"
    MSQLDatabase = "VSA2023"
    username = "DescomKasa"
    password = "D123456d*"
    connection_string = "DRIVER={SQL Server};SERVER=" + ServerName + ";DATABASE=" + MSQLDatabase + ";UID=" + username + ";PWD=" + password + ";charset=utf-8"
    params = urllib.parse.quote_plus(connection_string)
    engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
    # Güncelleme sorgusu
    query = f"UPDATE TBLISEMRI SET KAPALI = '{yeni_deger}' WHERE ISEMRINO = '{emir_no}'"
    # Sorguyu çalıştır
    with engine.begin() as connection:
        connection.execute(text(query))
    st.success('İş Emri güncellendi')
    #restart everything
    st.cache_data.clear()
    st.experimental_rerun()

if update:
    update_kapali_value(emir_no, yeni_deger)

