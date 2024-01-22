import streamlit as st
import pandas as pd

from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

st.title("Scraping Exceptions")

query = """
SELECT * FROM scraping_exceptions
"""

df_scraping_exceptions = pd.read_sql(query, con=engine)

st.dataframe(df_scraping_exceptions, hide_index=True)