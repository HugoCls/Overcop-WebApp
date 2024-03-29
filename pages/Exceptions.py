import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

conn = st.connection('overcop', type='sql')

st.title("Scraping Exceptions")

df_scraping_exceptions = pd.read_sql('SELECT * FROM `scraping_exceptions`', con=engine)

st.caption('All current Exceptions')
st.dataframe(df_scraping_exceptions, hide_index=True, width=1000)

Exceptions_Names = list(df_scraping_exceptions['Name'].unique())

df_Database = conn.query('SELECT * FROM `ov_Database`')

Database_Names = list(df_Database['Name'].unique())

pairs_to_add = st.multiselect(
    'Select pairs to add as an exception',
    Database_Names)

if st.button('Add'):
    with conn.session as s:
        for Name in pairs_to_add:
            try:
                s.execute(text(f'INSERT INTO scraping_exceptions (Name) VALUES (:name)'), {'name': Name})
                st.text(f"- Added '{Name}'*")
            except:
                st.text(f"- '{Name}' was already in exceptions")

        s.commit()
        st.rerun()

pairs_to_delete = st.multiselect(
    'Select pairs delete from exceptions table',
    Exceptions_Names)

if st.button('Delete'):
    with conn.session as s:
        for Name in pairs_to_delete:
            try:
                s.execute(text('DELETE FROM scraping_exceptions WHERE Name = :name'), {'name': Name})
                st.text(f"- Deleted '{Name}'")
            except Exception as e:
                st.text(f"- '{Name}' was not found in exceptions")

        s.commit()
        st.rerun()