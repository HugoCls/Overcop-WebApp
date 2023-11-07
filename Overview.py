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
    #initial_sidebar_state="expanded",
)

st.markdown("# Overview 📈")
st.sidebar.markdown("# Overview 📈")
custom_css = '''
<style>
    .palettecontainer {
        display: flex;
        align-items: center;
    }

    .palettecolordivcon {
        padding: 0;
        border: 0;
        width: auto;
    }

    .palettecolordiv {
        height: 96px;
        width: 20%;
    }

    .palettecolordiv, .palettecolordivc {
        color: white;
        float: left;
        margin: 0;
        padding: 0;
        text-align: center;
        text-shadow: 2px 2px 2px #333133;
    }

    .palettecolordivc {
        height: 20px;
        width: 20%;
    }
</style>
'''

# Définissez les couleurs et les explications
colors = [["#10ef99",' '], ["#7ef6c8", '‎'], ["#b7ffe3", ' ‎'], ["#e0fff3", '‎ '], ["#f8fffc",'  '], ["#06e0f8", '‎  '], ["#7ee9f5", ' ‎ '], ["#adf0f7", '  ‎'], ["#dafafd", '‎‎'], ["#f6feff",'‎‎ ']]

descriptions = ['1-2j', '2-3j', '3-5j', '5-10j', '10j+']

palette_html = f'''
<div class="palettecontainer">
    <div class="palettecolordivc" style="background-color: black"></div>
    <span style="margin-left: 12px; text-align: center;">No update</span>
</div>
<div class="palettecontainer">
    <div class="palettecolordivc" title="{descriptions[0]}" style="background-color:{colors[0][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[1]}" style="background-color:{colors[1][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[2]}" style="background-color:{colors[2][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[3]}" style="background-color:{colors[3][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[4]}" style="background-color:{colors[4][0]}"></div>
    <span style="margin-left: 12px; text-align: center;">Found <b>size</b></span>
</div>
<div class="palettecontainer">
    <div class="palettecolordivc" title="{descriptions[0]}" style="background-color:{colors[5][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[1]}" style="background-color:{colors[6][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[2]}" style="background-color:{colors[7][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[3]}" style="background-color:{colors[8][0]}"></div>
    <div class="palettecolordivc" title="{descriptions[4]}" style="background-color:{colors[9][0]}"></div>
    <span style="margin-left: 12px; text-align: center;">Found <b>shoe only</b></span>
</div>
'''

st.markdown(custom_css, unsafe_allow_html=True)

st.sidebar.write(palette_html, unsafe_allow_html=True)
st.sidebar.write("**Newer >>> Older**")

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
    for color in colors:
        if state == color[1]:
            return f'background-color: {color[0]}'

    return 'background-color: black'

def determine_color(state_and_last_date):
    if state_and_last_date is None:
        return ''

    else:
        [state, last_date_str] = state_and_last_date.split(':')

        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()

        date_difference = most_recent_date - last_date

        thresholds = [timedelta(days=2), timedelta(days=3), timedelta(days=5), timedelta(days=10)]

        if state == "custom":
            if date_difference < thresholds[1]:
                return colors[0][1]
            elif thresholds[0] <= date_difference <= thresholds[1]:
                return colors[1][1]
            elif thresholds[1] <= date_difference <= thresholds[2]:
                return colors[2][1]
            elif thresholds[2] <= date_difference <= thresholds[3]:
                return colors[3][1]
            else:
                return colors[4][1]

        elif state == "None" or state == "displayed":
            if date_difference < thresholds[1]:
                return colors[5][1]
            elif thresholds[0] <= date_difference <= thresholds[1]:
                return colors[6][1]
            elif thresholds[1] <= date_difference <= thresholds[2]:
                return colors[7][1]
            elif thresholds[2] <= date_difference <= thresholds[3]:
                return colors[8][1]
            else:
                return colors[9][1]
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

    df = df.style.map(add_colors, subset=columns).hide(level=1)

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