import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

st.title("Sales")

uploaded_file = st.file_uploader("uploaded file",label_visibility="collapsed", type=['csv'])

if uploaded_file is not None:  

    df = pd.read_csv(uploaded_file)
    df = df[["Paid at", "Total"]].dropna()

    df['Paid at'] = df['Paid at'].apply(lambda x: x[:10])

    df['Paid at'] = pd.to_datetime(df['Paid at'])

    df.sort_values('Paid at', inplace=True)

    daily_sales = df.groupby('Paid at')['Total'].sum()

    total_sales = df.groupby('Paid at')['Total'].sum().cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_sales.index, 
        y=daily_sales.values,
        mode='lines+markers',
        line=dict(color='black', width=2, dash='dot'),
        marker_color='blue',
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales"
    )
    
    fig.update_traces(marker={'size': 8})

    st.markdown(f"**Cumulated sales by day**")
    
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=total_sales.index, 
        y=total_sales.values,
        mode='lines+markers',
        line=dict(color='black', width=2, dash='dot'),
        marker_color='blue',
    ))

    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales"
    )
    
    fig2.update_traces(marker={'size': 8})

    st.markdown(f"**Total cumulated sales**")
    
    st.plotly_chart(fig2, use_container_width=True)