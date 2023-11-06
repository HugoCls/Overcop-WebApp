import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

def format_name(name):
    name = name.lower().replace('\u00a0',' ').replace('-',' ').replace('_',' ').replace('copy of ','').replace('copie de ', '')

    for mark in ['ugg', 'yeezy', 'nike', 'new balance', 'air jordan', 'jordan']:

        name = name.replace(f'{mark} {mark}', f'{mark}')

    return name

def replace_with_spaces(value):
    return ' '  # Remplace la valeur par un espace

st.set_page_config(
    page_title="Overcop Data",
    page_icon="data/icon.jpg",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("# Overview 📈")
st.sidebar.markdown("# Overview 📈")

df_stock = pd.read_sql("SELECT * FROM `Database`", con=engine)

df_logs = pd.read_sql("SELECT * FROM `Priceslogs`", con=engine)

most_recent_date = df_logs['ProcessingDate'].max()

# Groupement des tailles par nom
grouped = df_stock.groupby('Name')['Size'].apply(list).reset_index()

name_size_dict = dict(zip(grouped['Name'], grouped['Size']))

# Supprimer les valeurs "None" des listes dans le dictionnaire
name_size_dict = {name: [size for size in sizes if size is not None] for name, sizes in name_size_dict.items()}


N = max(len(sizes) for sizes in name_size_dict.values())

def add_colors(state):

    green_colors = ["#85ff99", "#407d4a", "#294f2f"]

    blue_colors = ["#83c8fc", "#4c7391", "#314b5e"]


    if state == ' ':
        color = blue_colors[0]
    elif state == '  ':
        color = blue_colors[1]
    elif state == '   ':
        color = blue_colors[2]
    elif state == '‎':
        color = green_colors[0]
    elif state == ' ‎':
        color = green_colors[1]
    elif state == '  ‎':
        color = green_colors[2]
    else:
        color = 'black'

    return f'background-color: {color}'

def determine_color(state_and_last_date):
    if state_and_last_date is None:
        return ''

    else:
        [state, last_date_str] = state_and_last_date.split(':')

        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()

        date_difference = most_recent_date - last_date

        thresholds = [timedelta(days=2), timedelta(days=5)]

        if state == "None" or state == "displayed":
            if date_difference > thresholds[1]:
                return '   '
            elif thresholds[0] <= date_difference <= thresholds[1]:
                return '  '
            else:
                return ' '

        elif state == "custom":
            if date_difference > thresholds[1]:
                return "  ‎"
            elif thresholds[0] <= date_difference <= thresholds[1]:
                return " ‎"
            else:
                return "‎"
        else:
            return ''
    
for name in name_size_dict:

    columns = name_size_dict[name]

    row = {}

    for column in columns:
        filtered_df = df_logs[(df_logs['Name'] == name) & (df_logs['Size'] == column)].sort_values(by='ProcessingDate', ascending=False)

        if not filtered_df.empty:        
            state_and_last_date = f"{filtered_df.iloc[0]['State']}:{filtered_df.iloc[0]['ProcessingDate']}"
        
        else:
            state_and_last_date = None

        row[column] = [determine_color(state_and_last_date)]

    df = pd.DataFrame(row)

    df = df.style.applymap(add_colors, subset=columns).hide(level=1)

    col1, col2 = st.columns([1, 8])
    
    #with col1:
    #    st.markdown(format_name(name).title())
    
    with col1:
        if len(df_stock[df_stock['Name'] == name]) >= 1:
            image_url = df_stock[df_stock['Name'] == name].iloc[0]['Image']
        else:
            image_url = "https://t4.ftcdn.net/jpg/04/73/25/49/360_F_473254957_bxG9yf4ly7OBO5I0O5KABlN930GwaMQz.jpg"

        st.image(image_url, caption=format_name(name).title(), use_column_width=True)
        
    with col2:
        st.dataframe(df, hide_index=True)
        