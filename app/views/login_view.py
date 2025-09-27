import mysql.connector
from mysql.connector import Error
import streamlit as st
from pathlib import Path
from app.auth import verificar_login  # sua função de verificação atual
from database.connection import conectar
import base64

def get_cargo_usuario(cargo_id):
    """Puxa o cargo do funcionário a partir do ID."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM cargos WHERE id = %s", (cargo_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result["nome"]
    return None

def mostrar_login():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "login_style.css"

    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Font Awesome
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    logo_path = Path("images/logomarca1t.png")
    with open(logo_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <style>
        .login-logo {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 450px;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        .login-title {{
            pointer-events: none;
        }}
        </style>
        <img src="data:image/png;base64,{encoded}" class="login-logo">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="login-title">Acesso ao Sistema</div>', unsafe_allow_html=True)

            st.markdown('<label><i class="fa-solid fa-user"></i> Email</label>', unsafe_allow_html=True)
            email = st.text_input("", placeholder="Digite seu email", label_visibility="collapsed")

            st.markdown('<span class="input-gap"></span>', unsafe_allow_html=True)

            st.markdown('<label><i class="fa-solid fa-lock"></i> Senha</label>', unsafe_allow_html=True)
            senha = st.text_input("", type="password", placeholder="Digite sua senha", label_visibility="collapsed")

            submit = st.form_submit_button("Entrar")

        if submit:
            usuario = verificar_login(email, senha)
            if usuario:
                # Pega o cargo do funcionário
                cargo = get_cargo_usuario(usuario["cargo_id"])

                # Salva usuário logado e cargo na sessão
                st.session_state["logado"] = True
                st.session_state["usuario"] = {
                    "id": usuario["id"],
                    "nome": usuario["nome"],
                    "email": usuario["email"],
                    "loja": usuario["loja"],
                    "cargo_id": usuario["cargo_id"],  # cargo do funcionário logado
                    "cargo": cargo
                }
                st.rerun()
            else:
                st.error("Email ou senha incorretos")
