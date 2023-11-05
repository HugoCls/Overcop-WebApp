import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')

df_stock = pd.read_sql("SELECT * FROM Database", con=engine)

df_logs = pd.read_sql("SELECT * FROM Priceslogs", con=engine)

chaussures = df_stock['Name'].unique()

resume_df = pd.DataFrame(columns=["Size", "Last Update", "Current Price", "Nb of Updates"])

st.set_page_config(
    page_title="Overcop Data",
    page_icon="data/icon.jpg",
    layout="centered",
)

# Sidebar pour la sélection de la chaussure
st.sidebar.title("Historique des prix")

selected_chaussure = st.sidebar.selectbox("Sélectionnez une chaussure", chaussures)

sizes = df_stock[df_stock['Name'] == selected_chaussure]['Size'].unique()

# Afficher l'image de la chaussure
image_url = df_stock[df_stock['Name'] == selected_chaussure].iloc[0]['Image']

st.sidebar.image(image_url, caption=selected_chaussure, use_column_width=True)

# Filtrer le DataFrame en fonction de la chaussure sélectionnée
filtered_df_logs = df_logs[df_logs['Name'] == selected_chaussure]

filtered_df_stock = df_stock[df_stock['Name'] == selected_chaussure]

# Créer un graphique pour chaque taille avec des points reliés par des lignes
fig = go.Figure()

for size in filtered_df_stock['Size'].unique():
    
    size_data = filtered_df_logs[filtered_df_logs['Size'] == size]

    if len(size_data) >= 1:
        last_update = size_data['ProcessingDate'].max()
    else:
        last_update = None

    resume_line = {
        "Size": [size],
        "Last Update": [last_update],
        "Current Price": [filtered_df_stock[filtered_df_stock["Size"] == size]["Price"].iloc[0]],
        "Nb of Updates": [len(size_data)],
        }

    resume_df = pd.concat([pd.DataFrame(resume_line), resume_df], ignore_index=True)

    if len(size_data) >= 1:

        fig.add_trace(go.Scatter(
            x=size_data['ProcessingDate'],
            y=size_data['Price'],
            mode='lines+markers',
            name=f'Taille {size}',
        ))

fig.update_layout(
    title=f"Évolution des prix pour {selected_chaussure}",
    xaxis_title="Date",
    yaxis_title="Prix"
)

# Afficher le graphique
st.plotly_chart(fig)

st.markdown(resume_df.sort_values("Size", ascending=False).style.hide(axis="index").to_html(), unsafe_allow_html=True)