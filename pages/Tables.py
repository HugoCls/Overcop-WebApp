import streamlit as st
import pandas as pd
import os

from sqlalchemy import create_engine
from all_in_scrap import Scraping, get_pairs_to_scrap

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

df_logs = pd.read_sql("SELECT * FROM `Priceslogs`", con=engine)

df_stock = pd.read_sql("SELECT * FROM `ov_Database`", con=engine)

df_prices = pd.read_sql("SELECT * FROM `WTN_prices`", con=engine)

st.set_page_config(
    page_title="Overcop Data",
    page_icon="data:image/jpeg;base64,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",
    layout="wide",
)

st.markdown("# Tables :signal_strength:")
st.sidebar.markdown("# Tables :signal_strength:")

st.title("Correspondances")

uploaded_file = st.file_uploader("uploaded file",label_visibility="collapsed", type=['csv'])

if uploaded_file is not None:  

    df = pd.read_csv(uploaded_file)
    df["Name"] = df.groupby('Handle')['Vendor'].transform(lambda x: x.fillna(x.loc[x.notnull()].iloc[0])) + ' ' + df.groupby('Handle')['Title'].transform(lambda x: x.fillna(x.loc[x.notnull()].iloc[0]))
    df["Size"] = df["Option1 Value"]
        
    Scraper = Scraping()

    Scraper.scrap_pages()

    correspondances_df = get_pairs_to_scrap(df, Scraper.all_WTN_pairs)

    st.dataframe(correspondances_df)
    

st.title("Priceslogs")
st.dataframe(df_logs)

st.title("Database")
st.dataframe(df_stock)

st.title("🚧 In Construction 🚧")
st.title("Prices")
st.dataframe(df_prices)

folders = ''

dossier_parent = os.getcwd()

for dossier, sous_dossiers, fichiers in os.walk(dossier_parent):
    folders += f'Dossier : {dossier}\n'

    # Afficher tous les fichiers dans le dossier actuel
    for fichier in fichiers:
        chemin_fichier = os.path.join(dossier, fichier)
        folders += f'   Fichier : {chemin_fichier}\n'

    # Afficher les sous-dossiers du dossier actuel
    for sous_dossier in sous_dossiers:
        chemin_sous_dossier = os.path.join(dossier, sous_dossier)
        folders += f'   Sous-dossier : {chemin_sous_dossier}\n'

st.text_area("Files:", value=folders, height=min(600, folders.count('\n') + 1))