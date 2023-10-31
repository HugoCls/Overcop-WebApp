import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Overcop Data",
    page_icon="data/icon.jpg",
    layout="centered",
)

stock_data = [
    {"Name": "Chaussure A", "Size": 38, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
    {"Name": "Chaussure A", "Size": 39, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
    {"Name": "Chaussure A", "Size": 40, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
    {"Name": "Chaussure B", "Size": 38, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
    {"Name": "Chaussure B", "Size": 39, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
    {"Name": "Chaussure B", "Size": 40, "Price":120, "Image": "https://cdn.shopify.com/s/files/1/2358/2817/files/nike-dunk-low-wmns-cacao-wow_20628849_46151291_20482.png?v=1691768028&width=1940%201940w"},
]

# Données simulées
data_logs = [
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure A", "Size": 38, "Price": 100},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure A", "Size": 38, "Price": 95},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure A", "Size": 38, "Price": 97},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure A", "Size": 38, "Price": 98},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure A", "Size": 38, "Price": 102},
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure B", "Size": 38, "Price": 110},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure B", "Size": 38, "Price": 105},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure B", "Size": 38, "Price": 108},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure B", "Size": 38, "Price": 112},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure B", "Size": 38, "Price": 115},
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure A", "Size": 39, "Price": 120},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure A", "Size": 39, "Price": 118},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure A", "Size": 39, "Price": 125},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure A", "Size": 39, "Price": 123},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure A", "Size": 39, "Price": 130},
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure B", "Size": 39, "Price": 105},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure B", "Size": 39, "Price": 102},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure B", "Size": 39, "Price": 108},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure B", "Size": 39, "Price": 103},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure B", "Size": 39, "Price": 110},
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure A", "Size": 40, "Price": 95},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure A", "Size": 40, "Price": 98},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure A", "Size": 40, "Price": 100},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure A", "Size": 40, "Price": 96},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure A", "Size": 40, "Price": 102},
    {"ProcessingDate": "2023-01-01", "Name": "Chaussure B", "Size": 40, "Price": 98},
    {"ProcessingDate": "2023-01-02", "Name": "Chaussure B", "Size": 40, "Price": 102},
    {"ProcessingDate": "2023-01-03", "Name": "Chaussure B", "Size": 40, "Price": 100},
    {"ProcessingDate": "2023-01-04", "Name": "Chaussure B", "Size": 40, "Price": 105},
    {"ProcessingDate": "2023-01-05", "Name": "Chaussure B", "Size": 40, "Price": 98}
]

# Créer un DataFrame
df_stock = pd.DataFrame(stock_data)

# Sidebar pour la sélection de la chaussure
st.sidebar.title("Historique des prix")
chaussures = df_stock['Name'].unique()

selected_chaussure = st.sidebar.selectbox("Sélectionnez une chaussure", chaussures)

sizes = df_stock[df_stock['Name'] == selected_chaussure]['Size'].unique()


# Afficher l'image de la chaussure
image_url = df_stock[df_stock['Name'] == selected_chaussure].iloc[0]['Image']
st.sidebar.image(image_url, caption=selected_chaussure, use_column_width=True)

df_logs = pd.DataFrame(data_logs)

resume_df = pd.DataFrame(columns=["Size", "Last Update", "Current Price", "Nb of Updates"])

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