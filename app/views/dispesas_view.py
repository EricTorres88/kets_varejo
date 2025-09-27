import mysql.connector
from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

def cadastrar_despesa(tipo, valor, estado, data_pagamento = None, data_vencimento = None):
    conn = conectar()
    cursor = conn.cursor()
    if estado == "Pago" and data_pagamento:
        cursor.execute("""
            INSERT INTO despesas (tipo, valor, data_pagamento, estado, data_vencimento)
            VALUES (%s, %s, %s, %s, %s)
        """, (tipo, valor, data_pagamento, estado, data_vencimento))
    else:
        cursor.execute("""
            INSERT INTO despesas (tipo, valor, estado, data_vencimento)
            VALUES (%s, %s, %s, %s)
        """, (tipo, valor, estado, data_vencimento))
    conn.commit()
    conn.close()
    st.success("Despesa registrada com sucesso!")

def editar_despesa(despesa_id, novo_estado, nova_data_pagamento = None):
    conn = conectar()
    cursor = conn.cursor()

    if novo_estado == "Pago" and nova_data_pagamento:
        cursor.execute("""
            UPDATE despesas
            SET estado = %s, data_pagamento = %s
            WHERE id = %s
        """, (novo_estado, nova_data_pagamento, despesa_id))
    else:
        cursor.execute("""
            UPDATE despesas
            SET estado = %s, data_pagamento = NULL
            WHERE id = %s
        """, (novo_estado, despesa_id))
    conn.commit()
    conn.close()
    st.success("Despesa alterada com sucesso!")
    st.rerun()

def excluir_despesa(despesa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM despesas WHERE id = %s", (despesa_id,))
    conn.commit()
    conn.close()
    st.success("Despesa removida com sucesso!")
    st.rerun()

def mostrar_despesas_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "despesas_style.css"
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
    
    st.title("Cadastro e Gerenciamento de Despesas")
    if st.button("➕ Cadastrar nova despesa", key="botao_cadastro_despesa"):
        st.session_state["abrir_cadastro_desp"] = not st.session_state.get("abrir_cadastro_desp", False)
    
    if st.session_state.get("abrir_cadastro_desp", False):
        with st.expander("📋 Formulário de Cadastro de despesa", expanded=True):
            with st.form("form_cadastro", clear_on_submit=True):
                st.markdown('<label class="form-label" for="tipo"><i class="fa-solid fa-calculator"></i> Tipo de despesa</label>', unsafe_allow_html=True)
                tipo = st.text_input("", key="tipo_cadastro", placeholder="Ex: Conta de água", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="valor"><i class="fa-solid fa-sack-dollar"></i> Valor da despesa</label>', unsafe_allow_html=True)
                valor = st.number_input("", min_value=0.0, format="%.2f", key="valor_cadastro", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="estado"><i class="fa-solid fa-folder"></i> Estado</label>', unsafe_allow_html=True)
                estado = st.selectbox("",  ["Em aberto", "Pago"], key="estado_cadastro", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="data"><i class="fa-solid fa-calendar"></i> Data de vencimento</label>', unsafe_allow_html=True)
                data_vencimento = st.date_input("Opcional", key="venc_despesa", label_visibility="collapsed", value=None)
                
                data_pagamento = None
                if estado == "Pago":
                    data_pagamento = st.date_input("Data de Pagamento", key="pagamento_despesa")

                submitted = st.form_submit_button("Cadastrar")

            if submitted:
                if tipo and valor:
                    cadastrar_despesa(tipo, valor, estado, data_pagamento, data_vencimento)
                    del st.session_state["abrir_cadastro_desp"]
                    st.rerun()
                else:
                    st.error("Preencha ao menos o tipo e valor da despesa.")

    st.markdown("---")
    st.markdown('<h3 class="listaprodutos"><i class="fa-solid fa-clipboard-list"></i> Lista de Despesas</h3>', unsafe_allow_html=True)

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM despesas")
    despesas = cursor.fetchall()
    conn.close()

    if not despesas:
        st.info("Nenhuma despesa cadastrada ainda.")
    else:
        for desp in despesas:
            st.markdown(f'''
            <div class="despesa-card">
                <p class="desp-nome"><i class="fa-solid fa-calculator"></i> {desp["tipo"]}</p>
                <div class="despesa-info-container">
                    <p><i class="fa-solid fa-sack-dollar"></i> Valor: {desp["valor"]}</p>
                    <p><i class="fa-solid fa-qrcode"></i> Estado: {desp["estado"]}</p>
                </div>
            </div>
''', unsafe_allow_html=True)
            #condição fora da string
            if desp['data_pagamento']:
                st.markdown(f'''
                <div class="pagamento-card">
                    <p><i class="fa-solid fa-calendar"></i> Pagamento da conta: {desp['data_pagamento']}</p>
                </div>
            ''', unsafe_allow_html=True)
            if desp['data_vencimento']:
                st.markdown(f'''
                <div class="vencimento-card">
                    <p><i class="fa-solid fa-calendar"></i> Vencimento da conta: {desp['data_vencimento']}</p>
                </div>
            ''', unsafe_allow_html=True)
                
            col_alterar, _, col_deletar, _ = st.columns([1, 0.1, 1, 8])

            with col_alterar:
                if st.button("✏️ Alterar Status", key=f"alt_status_{desp['id']}"):
                    st.session_state[f"mostrar_update_status_{desp['id']}"] = not st.session_state.get(f"mostrar_update_status_{desp['id']}", False)
                    st.session_state[f"mostrar_delete_despesa_{desp['id']}"] = False

            with col_deletar:
                if st.button("🗑️ Deletar", key=f"deletar_despesa_{desp['id']}"):
                    st.session_state[f"mostrar_delete_despesa_{desp['id']}"] = not st.session_state.get(f"mostrar_delete_despesa_{desp['id']}", False)
                    st.session_state[f"mostrar_update_status_{desp['id']}"] = False

            if st.session_state.get(f"mostrar_update_status_{desp['id']}", False):
                with st.form(f"form_status_{desp['id']}"):
                    nova_situacao = st.radio(
                        "Atualizar estado da despesa",
                        ["Em aberto", "Pago"],
                        index=0 if desp['estado'] == "Em aberto" else 1
                    )
                    nova_data_pagamento = None
                    atualizar_submit = st.form_submit_button("Confirmar atualização")
                    if nova_situacao == "Pago":
                        nova_data_pagamento = st.date_input("Data de Pagamento", key=f"data_pagamento_edit_{desp['id']}")
                    if atualizar_submit:
                        del st.session_state[f"mostrar_update_status_{desp['id']}"]
                        editar_despesa(desp['id'], nova_situacao, nova_data_pagamento)

            if st.session_state.get(f"mostrar_delete_despesa_{desp['id']}", False):
                with st.form(f"form_deletar_{desp['id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que deseja deletar esta despesa? Essa ação não pode ser recuperada.",
                        ("Sim", "Não"),
                        index=1,
                        key=f"confirma_delete_{desp['id']}"
                    )
                    deletar_submit = st.form_submit_button("Confirmar Exclusão")
                    if deletar_submit:
                        del st.session_state[f"mostrar_delete_despesa_{desp['id']}"]

                        if confirmar_delete == "Sim":
                            excluir_despesa(desp['id'])
                        elif confirmar_delete == "Não":
                            st.rerun()
                        else:
                            st.warning("Selecione uma opção antes de confirmar")

        st.markdown('</div>', unsafe_allow_html=True)
