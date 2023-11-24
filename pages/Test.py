import logging as log
import streamlit as st
import os

if st.button('Folders & Files'):
    st.text(f"{os.getcwd()}")

    for dossier_parent, dossiers, fichiers in os.walk(os.getcwd()):
        for dossier in dossiers:
            print(os.path.join(dossier_parent, dossier))
        for fichier in fichiers:
            print(os.path.join(dossier_parent, fichier))


if st.button('Log test'):
    print("TEST")
    log.info("TEST")
    print("HELLO")