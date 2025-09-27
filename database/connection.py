import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

def conectar():
    try:
        if hasattr(st, "secrets") and "DB_HOST" in st.secrets:
            conexao = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=os.getenv("DB_PORT")
            )
        else:
            # Se estiver rodando localmente, usa variáveis do .env
            conexao = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=os.getenv("DB_PORT")
            )

        if conexao.is_connected():
            return conexao

    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

    return None
