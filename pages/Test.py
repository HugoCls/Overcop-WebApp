import logging as log
import streamlit as st
import os

st.text(f"{os.getcwd()}")

for dossier_parent, dossiers, fichiers in os.walk(os.getcwd()):
    for dossier in dossiers:
        print(os.path.join(dossier_parent, dossier))
    for fichier in fichiers:
        print(os.path.join(dossier_parent, fichier))


if st.button('LOG'):
    log.info("TEST")
    print("TEST")