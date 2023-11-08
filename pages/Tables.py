import streamlit as st
import pandas as pd

from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

df_logs = pd.read_sql("SELECT * FROM `Priceslogs`", con=engine)

df_stock = pd.read_sql("SELECT * FROM `Database`", con=engine)

st.set_page_config(
    page_title="Overcop Data",
    page_icon="../data/icon.jpg",
    layout="wide",
)

st.markdown("# Tables :signal_strength:")
st.sidebar.markdown("# Tables :signal_strength:")

st.title("Priceslogs")
st.dataframe(df_logs)

st.title("Database")
st.dataframe(df_stock)