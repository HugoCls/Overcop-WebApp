import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from sqlalchemy import create_engine

engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/overcop')
    
def format_name(name):
    name = name.lower().replace('\u00a0',' ').replace('-',' ').replace('_',' ').replace('copy of ','').replace('copie de ', '')

    for mark in ['ugg', 'yeezy', 'nike', 'new balance', 'air jordan', 'jordan']:

        name = name.replace(f'{mark} {mark}', f'{mark}')

    return name

st.markdown("# Shoes 👟")
st.sidebar.markdown("# Shoes 👟")

df_stock = pd.read_sql("SELECT * FROM `Database`", con=engine)

query = """
WITH all_logs AS (
SELECT
	*,
	ROW_NUMBER() OVER (PARTITION BY ProcessingDate, Name, Size ORDER BY ID DESC) AS rn
FROM Priceslogs
)
SELECT * FROM all_logs WHERE rn = 1
"""

df_logs = pd.read_sql(query, con=engine)

# Appliquez la fonction format_name aux colonnes Name de df_stock et df_logs
df_stock['Name'] = df_stock['Name'].apply(lambda x: format_name(x).title() if pd.notna(x) else x)

df_logs['Name'] = df_logs['Name'].apply(lambda x: format_name(x).title() if pd.notna(x) else x)

chaussures = df_stock['Name'].unique()

resume_df = pd.DataFrame(columns=["Size", "Last Update", "Current Price", "Nb of Updates"])

# Sidebar pour la sélection de la chaussure
st.sidebar.title("Historique des prix")

# Divisez la barre latérale en deux colonnes
col1, col2 = st.sidebar.columns([3, 1])

# Première boîte de sélection pour la chaussure
selected_chaussure = col1.selectbox("Sélectionnez une chaussure", chaussures)

sizes = df_stock[df_stock['Name'] == selected_chaussure]['Size'].unique()

# Deuxième boîte de sélection pour la taille
selected_size = col2.selectbox("Taille", sizes)

if len(df_stock[df_stock['Name'] == selected_chaussure]) >= 1:
    image_url = df_stock[df_stock['Name'] == selected_chaussure].iloc[0]['Image']
else:
    image_url = "https://t4.ftcdn.net/jpg/04/73/25/49/360_F_473254957_bxG9yf4ly7OBO5I0O5KABlN930GwaMQz.jpg"

st.sidebar.image(image_url, caption=selected_chaussure, use_column_width=True)

# Filtrer le DataFrame en fonction de la chaussure sélectionnée
filtered_df_logs = df_logs[df_logs['Name'] == selected_chaussure]

filtered_df_stock = df_stock[df_stock['Name'] == selected_chaussure]

# Créer un graphique pour chaque taille avec des points reliés par des lignes
fig = go.Figure()

selected_size_data = filtered_df_logs[filtered_df_logs['Size'] == selected_size]

if len(selected_size_data) >= 1:

    fig.add_trace(go.Scatter(
        x=selected_size_data['ProcessingDate'],
        y=selected_size_data['Price'],
        mode='lines+markers',
        name=f'Taille {selected_size}',
        hovertemplate='%{y:.2f}€',  # Personnalisez le texte de survol ici
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Prix"
    )
    st.markdown(f"**Évolution des prix pour {selected_chaussure}, {selected_size}**")
    
    st.plotly_chart(fig, use_container_width=True, theme=None)
    
else:
    st.image("https://t4.ftcdn.net/jpg/04/72/65/73/360_F_472657366_6kV9ztFQ3OkIuBCkjjL8qPmqnuagktXU.jpg", caption=f"Évolution des prix pour {selected_chaussure}, {selected_size}")

for size in filtered_df_stock['Size'].unique():
    
    if size is not None:
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

st.markdown("**Résumé**")

st.markdown(resume_df.sort_values("Size", ascending=False).style.hide(axis="index").to_html(), unsafe_allow_html=True)