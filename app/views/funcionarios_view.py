import mysql.connector
from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

def editar_funcionario(usuario_id, novo_nome, novo_cargo_id, novo_telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET nome = %s, cargo_id = %s, telefone = %s
        WHERE id = %s
    """, (novo_nome, novo_cargo_id, novo_telefone, usuario_id))

    conn.commit()
    conn.close()
    st.success("Funcionário atualizado com sucesso!")
    st.rerun()

def excluir_funcionario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
    conn.commit()
    conn.close()
    st.warning("Usuário deletado com sucesso!")
    st.rerun()

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
    st.markdown('<h3 class="listafunc"><i class="fa-solid fa-clipboard-list"></i> Lista de Funcionários</h3>', unsafe_allow_html=True)
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.telefone, u.cargo_id, c.nome AS cargo
        FROM usuarios u
        LEFT JOIN cargos c ON u.cargo_id = c.id
        ORDER BY u.nome
    """)
    funcionarios = cursor.fetchall()
    # Buscar cargos disponíveis
    cursor.execute("SELECT id, nome FROM cargos")
    cargos = cursor.fetchall()
    conn.close()

    # Criar listas/dicionários de cargos
    nomes_cargos = [c["nome"] for c in cargos]
    cargo_dict = {c["nome"]: c["id"] for c in cargos}

    if not funcionarios:
        st.info("Nenhum funcionário cadastrado.")
        return
    
    for func in funcionarios:
        st.markdown(f'''
        <div class="func-card">
            <p class="func-nome"><i class="fa-solid fa-person"></i> {func["nome"]}</p>
            <div class="func-info-container">
                <p><i class="fa-solid fa-id-card-clip"></i> Cargo: {func["cargo"]}</p>
                <p><i class="fa-solid fa-envelope"></i> Email: {func["email"]}</p>
                <p><i class="fa-solid fa-phone"></i> Telefone: {func["telefone"]}</p>
            </div>
        ''', unsafe_allow_html=True)

        cargo_logado_id = st.session_state["usuario"]["cargo_id"]

        if cargo_logado_id == 1:
            col_alterar, _,col_deletar, _ = st.columns([1, 0.1, 1, 8])
            with col_alterar:
                if st.button("✏️ Alterar", key=f"editar_func_{func['id']}"):
                    st.session_state[f"mostrar_editar_func_{func['id']}"] = not st.session_state.get(f"mostrar_editar_func_{func['id']}", False)
                    st.session_state[f"mostrar_deletar_func_{func['id']}"] = False
            with col_deletar:
                if st.button("🗑️ Deletar", key=f"deletar_func_{func['id']}"):
                    st.session_state[f"mostrar_deletar_func_{func['id']}"] = not st.session_state.get(f"mostrar_deletar_func_{func['id']}", False)
                    st.session_state[f"mostrar_editar_func_{func['id']}"] = False

            if st.session_state.get(f"mostrar_editar_func_{func['id']}", False):
                with st.expander(f"✏️ Alterar dados de {func['nome']}", expanded=True):
                    with st.form(f"form_editar_{func['id']}"):
                        st.markdown('<label class="form-label"><i class="fa-solid fa-person"></i> Novo nome</label>', unsafe_allow_html=True)
                        novo_nome = st.text_input("", value=func["nome"], key=f"nome_{func['id']}", label_visibility="collapsed")

                        st.markdown('<label class="form-label"><i class="fa-solid fa-id-card-clip"></i> Novo cargo</label>', unsafe_allow_html=True)
                        novo_cargo_nome = st.selectbox(
                            "",
                            options=nomes_cargos,
                            index=nomes_cargos.index(func["cargo"]) if func["cargo"] in nomes_cargos else 0,
                            key=f"cargo_{func['id']}"
                        )
                        novo_cargo_id = cargo_dict[novo_cargo_nome]
                        st.markdown('<label class="form-label"><i class="fa-solid fa-phone"></i> Novo telefone</label>', unsafe_allow_html=True)
                        novo_telefone = st.text_input("", value=func["telefone"], key=f"telefone_{func['id']}", label_visibility="collapsed")

                        confirmar = st.radio(
                            "Deseja realmente modificar os dados do funcionário?",
                            ("Sim", "Não"),
                            index=1,
                            key=f"confirma_edicao_{func['id']}"
                        )
                        if st.form_submit_button("Confirmar Alteração"):
                            del st.session_state[f"mostrar_editar_func_{func['id']}"]
                            if confirmar == "Sim":
                                editar_funcionario(func['id'], novo_nome.strip(), novo_cargo_id, novo_telefone.strip())
                            else:
                                st.rerun()
            # Formulário de exclusão
            if st.session_state.get(f"mostrar_deletar_func_{func['id']}", False):
                with st.form(f"form_deletar_func_{func['id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que deseja deletar o funcionário? Esses dados não podem ser recuperados.",
                        ("Sim", "Não"),
                        index=1,
                        key=f"confirma_delete_func_{func['id']}"
                    )
                    if st.form_submit_button("Confirmar Exclusão"):
                        del st.session_state[f"mostrar_deletar_func_{func['id']}"]
                        if confirmar_delete == "Sim":
                            excluir_funcionario(func['id'])
                        else:
                            st.rerun()

            # Fechando o cartão só no final
            st.markdown('</div>', unsafe_allow_html=True)
            
