import mysql.connector
from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

# Função para cadastrar um cliente
def cadastrar_cliente(nome, endereco, telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, endereco, telefone) VALUES (%s, %s, %s)", (nome, endereco, telefone))
    conn.commit()
    conn.close()
    st.success("Cliente cadastrado com sucesso!")

# Função para atualizar um cliente
def atualizar_cliente(cliente_id, novo_nome, novo_endereco, novo_telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes 
        SET nome = %s, endereco = %s, telefone = %s 
        WHERE id = %s
    """, (novo_nome, novo_endereco, novo_telefone, cliente_id))
    conn.commit()
    conn.close()
    st.success("Cliente atualizado com sucesso!")
    st.rerun()

# Função para deletar um cliente
def deletar_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    conn.commit()
    conn.close()
    st.warning("Cliente deletado com sucesso!")
    st.rerun()

# Função principal da tela de clientes
def mostrar_clientes_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "clientes_style.css"

    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        .stApp {
            }
    </style>
""", unsafe_allow_html=True)
    
    st.title("Cadastro e Gerenciamento de Clientes")

    if st.button('➕ Cadastrar novo cliente', key="botao_cadastro"):
        st.session_state["abrir_cadastro"] = not st.session_state.get("abrir_cadastro", False)

    if st.session_state.get("abrir_cadastro", False):
        with st.expander("📋 Formulário de Cadastro", expanded=True):
            with st.form("form_cadastro", clear_on_submit=True):
                st.markdown('<label class="form-label" for="nome"><i class="fa-solid fa-person"></i> Nome</label>', unsafe_allow_html=True)
                nome = st.text_input("", key="nome_cadastro", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="endereco"><i class="fa-solid fa-house"></i> Endereço</label>', unsafe_allow_html=True)
                endereco = st.text_input("", key="endereco_cadastro", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="telefone"><i class="fa-solid fa-phone"></i> Telefone</label>', unsafe_allow_html=True)
                telefone = st.text_input("", key="telefone_cadastro", label_visibility="collapsed")
                submitted = st.form_submit_button("Cadastrar")

            if submitted:
                if nome and endereco and telefone:
                    cadastrar_cliente(nome, endereco, telefone)
                    del st.session_state["abrir_cadastro"]  # Fecha após cadastro
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos.")


    st.markdown("---")
    st.markdown('<h3 class="listaclientes"><i class="fa-solid fa-clipboard-list"></i> Lista de Clientes</h3>', unsafe_allow_html=True)


    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        for cliente in clientes:
            #começa aqui
            st.markdown(f'''
            <div class="cliente-card">
                <p class="cliente-nome"><i class="fa-solid fa-user"></i> {cliente["nome"]}</p>
                <div class="cliente-info-container">
                    <p><i class="fa-solid fa-house"></i> Endereço: {cliente["endereco"]}</p>
                    <p><i class="fa-solid fa-phone"></i> Telefone: {cliente["telefone"]}</p>
                </div>
            </div>
    ''', unsafe_allow_html=True)
            
            # Botões do Streamlit
            col_alterar, _, col_deletar, _ = st.columns([1, 0.1, 1, 8])
            with col_alterar:
                if st.button("✏️ Alterar", key=f"editar_{cliente['id']}"):
                    st.session_state[f"mostrar_edicao_{cliente['id']}"] = not st.session_state.get(f"mostrar_edicao_{cliente['id']}", False)
                    st.session_state[f"mostrar_delete_{cliente['id']}"] = False
            with col_deletar:
                if st.button("🗑️ Deletar", key=f"deletar_{cliente['id']}"):
                    st.session_state[f"mostrar_delete_{cliente['id']}"] = not st.session_state.get(f"mostrar_delete_{cliente['id']}", False)
                    st.session_state[f"mostrar_edicao_{cliente['id']}"] = False

            # Formulário de edição
            if st.session_state.get(f"mostrar_edicao_{cliente['id']}", False):
                with st.expander(f"✏️ Alterar dados de {cliente['nome']}", expanded=True):
                    st.markdown('<label class="form-label" for="nome"><i class="fa-solid fa-person"></i> Novo nome</label>', unsafe_allow_html=True)
                    novo_nome = st.text_input("", value=cliente["nome"], key=f"nome_{cliente['id']}", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="endereco"><i class="fa-solid fa-house"></i> Novo endereço</label>', unsafe_allow_html=True)
                    novo_endereco = st.text_input("", value=cliente["endereco"], key=f"endereco_{cliente['id']}", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="telefone"><i class="fa-solid fa-phone"></i> Novo telefone</label>', unsafe_allow_html=True)
                    novo_telefone = st.text_input("", value=cliente["telefone"], key=f"telefone_{cliente['id']}", label_visibility="collapsed")
                    with st.form(f"form_editar_{cliente['id']}"):
                        confirmar = st.radio(
                            "Deseja realmente modificar os dados do cliente?",
                            ("Sim", "Não"),
                            index=0,
                            key=f"confirma_edicao_{cliente['id']}"
                        )
                        confirmar_submit = st.form_submit_button("Confirmar Alteração")
                        if confirmar_submit:
                            del st.session_state[f"mostrar_edicao_{cliente['id']}"]
                            if confirmar == "Sim":
                                if novo_nome.strip() and novo_endereco.strip() and novo_telefone.strip():
                                    atualizar_cliente(cliente['id'], novo_nome, novo_endereco, novo_telefone)
                                else:
                                    st.warning("Todos os campos são obrigatórios!")
                            elif confirmar == "Não":
                                st.rerun()
                            else:
                                st.warning("Selecione uma opção antes de confirmar.")

            # Formulário de exclusão
            if st.session_state.get(f"mostrar_delete_{cliente['id']}", False):
                with st.form(f"form_deletar_{cliente['id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que deseja deletar o cliente? Esses dados não podem ser recuperados.",
                        ("Sim", "Não"),
                        index=0,
                        key=f"confirma_delete_{cliente['id']}"
                    )
                    deletar_submit = st.form_submit_button("Confirmar Exclusão")
                    if deletar_submit:
                        del st.session_state[f"mostrar_delete_{cliente['id']}"]
                        if confirmar_delete == "Sim":
                            deletar_cliente(cliente['id'])
                            st.rerun()
                        elif confirmar_delete == "Não":
                            st.rerun()
                        else:
                            st.warning("Selecione uma opção antes de confirmar")

            # Fim do card
            st.markdown('</div>', unsafe_allow_html=True)

# Exportar a função para uso no main.py
