import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def conectar():
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT")),
            ssl_ca="ca.pem", #mudou aqui
            ssl_disabled=False
        )
        if conexao.is_connected():
            print("Conexão bem-sucedida!")
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

if __name__ == "__main__":
    conectar()