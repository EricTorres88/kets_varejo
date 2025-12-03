import mysql.connector
from mysql.connector import Error
from database.connection import conectar
import streamlit as st
from app.views.login_view import mostrar_login
from app.views.clientes_view import mostrar_clientes_view
from app.views.produtos_view import mostrar_produtos_view
from app.views.vendas_view import mostrar_vendas_view
from app.views.parcelas_view import mostrar_parcela_view
from app.views.funcionarios_view import mostrar_funcionarios_view
from app.views.dispesas_view import mostrar_despesas_view
from app.views.suporte_view import suporte_view
from pathlib import Path

st.set_page_config(page_title="Sistema varejo", layout="wide")

# Inicializa sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "menu_selecionado" not in st.session_state:
    st.session_state["menu_selecionado"] = None

if not st.session_state["logado"]:
    mostrar_login()
else:
    # CSS do dashboard e sidebar (mantendo o original)
    style_path = Path(__file__).resolve().parent / "app" / "styles" / "main_style.css"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
    <style>
        
    </style>
    """, unsafe_allow_html=True)
    

    st.sidebar.title("Menu")
    if st.sidebar.button("Clientes"):
        st.session_state["menu_selecionado"] = "Clientes"
    if st.sidebar.button("Funcionários"):
        st.session_state["menu_selecionado"] = "Funcionarios"
    if st.sidebar.button("Produtos"):
        st.session_state["menu_selecionado"] = "Produtos"
    if st.sidebar.button("Vendas"):
        st.session_state["menu_selecionado"] = "Vendas"
    if st.sidebar.button("Parcelas"):
        st.session_state["menu_selecionado"] = "Parcelas"
    if st.sidebar.button("Despesas"):
        st.session_state["menu_selecionado"] = "Despesas"
    if st.sidebar.button("Suporte"):
        st.session_state["menu_selecionado"] = "Suporte"

    if st.session_state["menu_selecionado"] is None:
        st.markdown(f"<div class='painel'>Painel {st.session_state.usuario['loja']}</div>", unsafe_allow_html=True)
        st.markdown(f"Bem-vindo(a), **{st.session_state.usuario['nome']}**!")
        
        st.markdown("""
        <div class='infom'>
            <p>
                Este é seu sistema de gestão e controle da sua loja.
                Aqui você pode gerenciar suas vendas, clientes, produtos e muito mais.
                \nBasta acessar o menu lateral e escolher o que gostaria de consultar.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Conteúdo do menu
    
    menu = st.session_state.get("menu_selecionado")
    if menu == "Clientes":
        mostrar_clientes_view()
    elif menu == "Funcionarios":
        mostrar_funcionarios_view()
    elif menu == "Produtos":
        mostrar_produtos_view()
    elif menu == "Vendas":
        mostrar_vendas_view()
    elif menu == "Parcelas":
        mostrar_parcela_view()
    elif menu == "Despesas":
        mostrar_despesas_view()
    elif menu == "Suporte":
        suporte_view()

    
    # Logout
    if st.sidebar.button("Sair", key="logout_button", type="primary"):
        st.session_state.clear()  # limpa tudo da sessão
        st.rerun()  # força a atualização imediata
        #st.session_state["logado"] = False
        #st.session_state["usuario"] = None
        #st.session_state["menu_selecionado"] = None
