#import logging as log
import streamlit as st
import os
import sys
import logging

log_dir = os.path.join(os.getcwd(), 'data')
log_file_path = os.path.join(log_dir, 'console.log')

st.write(log_file_path)

log = logging.getLogger(__name__)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Crée le répertoire s'il n'existe pas

if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as file:
        file.write("")

if st.button('Folders & Files'):
    st.text(f"{os.getcwd()}")

    for dossier_parent, dossiers, fichiers in os.walk(os.getcwd()):
        for dossier in dossiers:
            st.text(os.path.join(dossier_parent, dossier))
        for fichier in fichiers:
            st.text(os.path.join(dossier_parent, fichier))

"""
if len(log.getLogger('').handlers) < 2:  # Vérifiez le nombre de handlers pour éviter les doublons
    temp_file_handler = log.FileHandler('data/temp_logs.log')
    temp_file_handler.setLevel(log.INFO)
    temp_file_handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s] %(filename)s - %(message)s'))
    log.getLogger('').addHandler(temp_file_handler)
"""

if st.button('Log test'):
    log.info("TEST")

with open(log_file_path, 'r') as file:
    logs_content = file.read()

st.text_area("Logs temporaires:", value=logs_content, height=min(600, logs_content.count('\n') + 1))