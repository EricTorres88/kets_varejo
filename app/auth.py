import mysql.connector
from mysql.connector import Error
import bcrypt
from database.connection import conectar

def verificar_login(email, senha):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id ,nome, email, senha_hash, loja, cargo_id, telefone FROM usuarios WHERE email = %s", (email,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado:
            usuario = {
                'id': resultado[0],
                'nome': resultado[1],
                'email': resultado[2],
                'senha_hash': resultado[3],
                'loja': resultado[4],
                'cargo_id': resultado[5],
                'telefone': resultado[6]
            }
            if senha and bcrypt.checkpw(senha.encode(), usuario['senha_hash'].encode()):
                return usuario
        return None
    except Exception as e:
        print(f"⚠️ Erro ao verificar login: {e}")
        return "erro_banco"

