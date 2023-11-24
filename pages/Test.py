import logging as log
import streamlit as st
import os
import sys

log_dir = os.path.join(os.getcwd(), 'data')
log_file_path = os.path.join(log_dir, 'console.log')

st.write(log_file_path)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Crée le répertoire s'il n'existe pas

if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as file:
        file.write("")  # Crée le fichier s'il n'existe pas
    
with open(log_file_path, 'a') as f:
    f.write('This is a test')

if st.button('Folders & Files'):
    st.text(f"{os.getcwd()}")

    for dossier_parent, dossiers, fichiers in os.walk(os.getcwd()):
        for dossier in dossiers:
            st.text(os.path.join(dossier_parent, dossier))
        for fichier in fichiers:
            st.text(os.path.join(dossier_parent, fichier))

st.text(log_file_path)

st.text(os.path.exists(log_file_path))

log.basicConfig(filename=f'{os.getcwd()}/data/console.log', level=log.INFO, format='%(asctime)s [%(levelname)s] %(filename)s - %(message)s')

if len(log.getLogger('').handlers) < 2:  # Vérifiez le nombre de handlers pour éviter les doublons
    temp_file_handler = log.FileHandler('data/temp_logs.log')
    temp_file_handler.setLevel(log.INFO)
    temp_file_handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s] %(filename)s - %(message)s'))
    log.getLogger('').addHandler(temp_file_handler)

if st.button('Log test'):
    #print("TEST")
    log.info("TEST")
    #print("HELLO")

with open('data/console.log', 'r') as file:
    logs_content = file.read()

log.info("THIS IS A LOG")

st.text_area("Logs temporaires:", value=logs_content, height=min(600, logs_content.count('\n') + 1))