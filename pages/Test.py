import logging as log
import streamlit as st
import os
"""
if st.button('Folders & Files'):
    st.text(f"{os.getcwd()}")

    for dossier_parent, dossiers, fichiers in os.walk(os.getcwd()):
        for dossier in dossiers:
            print(os.path.join(dossier_parent, dossier))
        for fichier in fichiers:
            print(os.path.join(dossier_parent, fichier))

"""

log.basicConfig(filename='data/console.log', level=log.INFO, format='%(asctime)s [%(levelname)s] %(filename)s - %(message)s')

if len(log.getLogger('').handlers) < 2:  # Vérifiez le nombre de handlers pour éviter les doublons
    temp_file_handler = log.FileHandler('data/temp_logs.log')
    temp_file_handler.setLevel(log.INFO)
    temp_file_handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s] %(filename)s - %(message)s'))
    log.getLogger('').addHandler(temp_file_handler)
    
if st.button('Log test'):
    #print("TEST")
    log.info("TEST")
    #print("HELLO")