import streamlit as st
import pandas as pd
from sqlalchemy import text

conn = st.connection('overcop', type='sql')

st.title("Scraping Exceptions")

df_scraping_exceptions = conn.query('SELECT * FROM `scraping_exceptions`')

Exceptions_Names = list(df_scraping_exceptions['Name'].unique())

st.caption('All current Exceptions')
st.dataframe(df_scraping_exceptions, hide_index=True, width=1000)

df_Database = conn.query('SELECT * FROM `ov_Database`')

Database_Names = list(df_Database['Name'].unique())

col1, col2 = st.columns(2)

with col1:
    pairs_to_add = st.multiselect(
        'Select pairs to add as an exception',
        Database_Names)

with col2:
    if st.button('Add'):
        with conn.session as s:
            for Name in pairs_to_add:
                try:
                    sql_expression = text(f'INSERT INTO scraping_exceptions (Name) VALUES (:name)')
                    s.execute(sql_expression, {'name': Name})
                    st.text(f"Added **'{Name}'**")
                except:
                    st.text(f"*'{Name}'* was already in exceptions")

            s.commit()
            df_scraping_exceptions = conn.query('SELECT * FROM `scraping_exceptions`')

with col1:
    pairs_to_delete = st.multiselect(
        'Select pairs delete from exceptions table',
        Exceptions_Names)

with col2:
    if st.button('Delete'):
        with conn.session as s:
            for Name in pairs_to_delete:
                try:
                    s.execute('DELETE FROM scraping_exceptions WHERE Name = :name;', {'name': Name})
                    st.text(f"Deleted *'{Name}'*")
                except:
                    st.text(f"*'{Name}'* was not found in exceptions")

            s.commit()
            df_scraping_exceptions = conn.query('SELECT * FROM `scraping_exceptions`')