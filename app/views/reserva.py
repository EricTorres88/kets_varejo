import os
import streamlit as st
from pathlib import Path
from app.auth import verificar_login

def mostrar_login():
    st.markdown("""
    <style>
            /* Fundo da página */
            .stApp {
                background-color: #dff3ff;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
                
            div[data-testid="stForm"] {
                background: #ffff !important;
                padding: 3rem !important;
                border-radius: 12px !important;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
                width: 100% !important;
                max-width: 700px !important;
                color: black !important;
            }
                
            /* Título */
            h2 {
                color: #a8a6a6 !important;
                text-align: center !important;
                margin-bottom: 1.5rem !important;
                font-size: 26px;
                font-weight: bold;
                font-family: Arial;
            }
            
            /* Inputs */
            .stTextInput input {
                background-color: #f8f8f8 !important;
                border: 1px solid #f8f8f8 !important;
                border-radius: 6px !important;
                padding: 10px !important;
                color: #333 !important;
            }
            
            /* Labels */
            label {
                color: #333 !important;
                margin-bottom: -26px !important;
                display: block !important;
            }
            
            /* Botão */
            .stButton>button {
                width: 30%;
                padding: 8px;
                margin-top: 1rem;
                background-color: #38b6ff;
                color: white !important;
                border: none;
                border-radius: 8px;
                font-weight: bold !important;
                transition: all 0.3s ease !important;
            }
            
            /* Botão */
            .stButton>button:hover {
                width: 30%;
                padding: 8px;
                margin-top: 1rem;
                background-color: #107bb8;
                color: white !important;
                border: none;
                border-radius: 8px;
                font-weight: bold !important;
                transform: scale(1.02);
            }
            
    </style>
""",unsafe_allow_html=True)

    #layout centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        #formulário principal
        with st.form("login_form"):
            st.markdown("<h2>Acesso ao Sistema</h2>", unsafe_allow_html=True)

            st.markdown("<label>Email</label>", unsafe_allow_html=True)
            email = st.text_input("", placeholder="Digite seu email", label_visibility="collapsed")

            st.markdown("<label>Senha</label>", unsafe_allow_html=True)
            senha = st.text_input("", type="password", placeholder="Digite sua senha", label_visibility="collapsed")

            submit = st.form_submit_button("Entrar")

        
        if submit:
            usuario = verificar_login(email, senha)
            if usuario:
                st.session_state.logado = {
                    "logado": True,
                    "nome": usuario["nome"],
                    "email": usuario["email"],
                    "loja": usuario["loja"]
                }
                st.experimental_rerun()
            else:
                error_col1, error_col2, error_col3 = st.columns([1, 2, 1])
                with error_col2:
                    st.markdown("""
                    <div style='background-color: rgba(255,151,151, 0.8); color: #333; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ff2828; margin: 1rem; max-width: 100%; text-align: center; backdrop-filter: blur(5px); display: block'>
                        Email ou senha incorretos.
                    </div>
""", unsafe_allow_html=True)

#CLIENTES.PY
from mysql.connector import Error
import streamlit as st
from database.connection import conectar

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
    st.experimental_rerun()

# Função para deletar um cliente
def deletar_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    conn.commit()
    conn.close()
    st.warning("Cliente deletado com sucesso!")
    st.experimental_rerun()

# Função principal da tela de clientes
def mostrar_clientes_view():
    st.markdown("""
    <style>
        .stApp {
                background-color: #dff3ff;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
    </style>
""", unsafe_allow_html=True)
    
    st.title("Cadastro e Gerenciamento de Clientes")

    if st.button("➕ Cadastrar novo cliente", key="botao_cadastro"):
        st.session_state["abrir_cadastro"] = True

    if st.session_state.get("abrir_cadastro", False):
        with st.expander("📋 Formulário de Cadastro", expanded=True):
            with st.form("form_cadastro", clear_on_submit=True):
                nome = st.text_input("Nome", key="nome_cadastro")
                endereco = st.text_input("Endereço", key="endereco_cadastro")
                telefone = st.text_input("Telefone", key="telefone_cadastro")
                submitted = st.form_submit_button("Cadastrar")            

            if submitted:
                if nome and endereco and telefone:
                    cadastrar_cliente(nome, endereco, telefone)
                    del st.session_state["abrir_cadastro"]  # Fecha após cadastro
                    st.experimental_rerun()
                else:
                    st.error("Por favor, preencha todos os campos.")


    st.markdown("---")
    st.subheader("Lista de Clientes")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        for cliente in clientes:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{cliente['nome']}**")
                with col2:
                    st.write("")

                with st.expander(f"ℹ️ Ver informações de {cliente['nome']}"):
                    st.write(f"📍 Endereço: {cliente['endereco']}")
                    st.write(f"📞 Telefone: {cliente['telefone']}")

                if st.button("✏️ Alterar", key=f"editar_btn_{cliente['id']}"):
                    st.session_state[f"mostrar_edicao_{cliente['id']}"] = True
                
                if st.session_state.get(f"mostrar_edicao_{cliente['id']}", False):
                    with st.expander(f"✏️ Alterar dados de {cliente['nome']}", expanded=True):
                        novo_nome = st.text_input(f"Novo nome (ID {cliente['id']})", cliente['nome'], key=f"nome_{cliente['id']}")
                        novo_endereco = st.text_input("Novo endereço", cliente['endereco'], key=f"endereco_{cliente['id']}")
                        novo_telefone = st.text_input("Novo telefone", cliente['telefone'], key=f"telefone_{cliente['id']}")
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
                                    atualizar_cliente(cliente['id'], novo_nome, novo_endereco, novo_telefone)
                                elif confirmar == "Não":
                                    st.experimental_rerun()
                                else:
                                    st.warning("Selecione uma opção antes de confirmar.")

                # Criar botão que, ao clicar, ativa o formulário de deletar
                if st.button("🗑️ Deletar", key=f"deletar_btn_{cliente['id']}"):
                    st.session_state[f"mostrar_delete_{cliente['id']}"] = True

                # Mostrar o formulário de exclusão apenas se o botão foi clicado
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
                            # Sempre remover a flag antes de recarregar
                            del st.session_state[f"mostrar_delete_{cliente['id']}"]

                            if confirmar_delete == "Sim":
                                st.session_state[f"mostrar_delete_{cliente['id']}"] = False
                                deletar_cliente(cliente['id'])
                            elif confirmar_delete == "Não":
                                st.experimental_rerun()
                            else:
                                st.warning("Selecione uma opção antes de confirmar")
# Exportar a função para uso no main.py

#Funcionarios.py

from mysql.connector import Error
import streamlit as st
from pathlib import Path
from database.connection import conectar

def editar_funcionario(funcionario_id, novo_nome, novo_cargo, novo_telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE funcionarios
        SET cargo = %s
        WHERE id = %s
    """, (novo_cargo, funcionario_id))

    cursor.execute("""
        UPDATE usuarios
        SET nome = %s, telefone = %s
        WHERE funcionario_id = %s
    """, (novo_nome, novo_telefone, funcionario_id))

    conn.commit()
    conn.close()
    st.success("Funcionário atualizado com sucesso!")

def excluir_funcionario(usuario_id, funcionario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = %s AND funcionario_id = %s
    """, (usuario_id, funcionario_id))
    conn.commit()
    conn.close()
    st.warning("Usuário deletado com sucesso!")
    st.experimental_rerun()

def mostrar_funcionarios_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "funcionarios_style.css"

    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        
    </style>
    """, unsafe_allow_html=True)

    st.title("Gerenciamento de Funcionários")
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id, u.id AS usuario_id, u.nome, u.email, u.telefone, f.cargo
        FROM funcionarios f
        INNER JOIN usuarios u ON u.funcionario_id = f.id
        ORDER BY u.nome
    """)
    funcionarios = cursor.fetchall()
    conn.close()

    if not funcionarios:
        st.info("Nenhum funcionário cadastrado.")
        return
    else:
        for func in funcionarios:
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**Funcionário: {func['nome']}**")
                with col2:
                    st.write("")

                with st.expander(f"ℹ️ Detalhes do funcionário {func['nome']}"):
                    st.write(f"🛠️ Cargo: {func['cargo']}")
                    st.write(f"📧 Email: {func['email'] or '-'}")
                    st.write(f"📞 Telefone: {func['telefone'] or '-'}")

                    if st.button("✏️ Editar", key=f"editar_func_{func['id']}"):
                        st.session_state[f"mostrar_editar_func_{func['id']}"] = True
                    if st.session_state.get(f"mostrar_editar_func_{func['id']}", False):
                        with st.form(f"form_editar_func_{func['id']}"):
                            novo_nome = st.text_input("Nome", value=func['nome'])
                            novo_telefone = st.text_input("Telefone", value=func['telefone'] or "")
                            novo_cargo = st.selectbox("Cargo", ["Gerente", "Funcionário"], index=0 if func['cargo'] == 'Gerente' else 1)
                            btn_salvar = st.form_submit_button("Salvar alterações")

                            if btn_salvar:
                                if not novo_nome.strip():
                                    st.error("O nome não pode ficar vazio.")
                                else:
                                    editar_funcionario(func['id'], novo_nome.strip(), novo_cargo, novo_telefone.strip())
                                    del st.session_state[f"mostrar_editar_func_{func['id']}"]
                                    st.experimental_rerun()

                    if st.button("🗑️ Deletar", key=f"deletar_func_{func['id']}"):
                        st.session_state[f"mostrar_deletar_func_{func['id']}"] = True
                    if st.session_state.get(f"mostrar_deletar_func_{func['id']}", False):
                        with st.form(f"form_deletar_func_{func['id']}"):
                            confirmar_delete = st.radio(
                            "Tem certeza que deseja deletar este funcionário? Essa ação não pode ser desfeita.",
                            ("Sim", "Não"),
                            index=1,
                            key=f"confirma_delete_func_{func['id']}"
                            )
                            btn_confirmar_delete = st.form_submit_button("Confirmar Exclusão")
                            if btn_confirmar_delete:
                                del st.session_state[f"mostrar_deletar_func_{func['id']}"]
                                if confirmar_delete == "Sim":
                                    excluir_funcionario(usuario_id=func['usuario_id'], funcionario_id=func['id'])
                                elif confirmar_delete == "Não":
                                    st.experimental_rerun()
                                else:
                                    st.warning("Selecione uma opção antes de confirmar.")
