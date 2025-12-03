import mysql.connector
from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

def cadastrar_venda(cliente_id, produto_id, valor, forma_pagamento, parcelas = None, quantidade_comprada=1):
    conn = conectar()
    cursor = conn.cursor()

    #Inserir a venda na tabela vendas
    cursor.execute("""
        INSERT INTO vendas (cliente_id, produto_id, valor, forma_pagamento, parcelas, quantidade_comprada)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (cliente_id, produto_id, valor, forma_pagamento, parcelas, quantidade_comprada))

    #Captura o ID da venda recém-criada
    venda_id = cursor.lastrowid
    conn.commit()


    # Se a forma de pagamento for crédito, insere também na tabela fiado
    if forma_pagamento == "Crédito" and parcelas > 0:
        cursor.execute("""
            INSERT INTO fiado (venda_id, cliente_id, produto_id, valor_devido, parcelas_total, parcelas_pagas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (venda_id, cliente_id, produto_id, valor, parcelas, 0))

    #Subtrai do estoque do produto
    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - %s
        WHERE id = %s
    """, (quantidade_comprada, produto_id))
    
    conn.commit()
    conn.close()
    st.success("Venda cadastrada com sucesso!")

def atualizar_status_venda(venda_id, nova_situacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vendas
        SET situacao = %s
        WHERE id = %s
    """, (nova_situacao, venda_id))
    conn.commit()
    conn.close()
    st.rerun()

def excluir_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fiado WHERE venda_id = %s", (venda_id,))
    cursor.execute("DELETE FROM vendas WHERE id = %s", (venda_id,))
    conn.commit()
    conn.close()
    st.rerun()

def mostrar_vendas_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "vendas_style.css"
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
    
    st.title("Cadastro e Gerenciamento de Vendas")
    if st.button("➕ Registrar nova venda", key="botao_cadastro_venda"):
        st.session_state["abrir_cadastro_venda"] = not st.session_state.get("abrir_cadastro_venda", False)

    if st.session_state.get("abrir_cadastro_venda", False):
        with st.expander("📋 Formulário de Venda", expanded=True):
            #with st.form("form_venda", clear_on_submit=True):
                conn = conectar()
                cursor = conn.cursor(dictionary=True)

                #buscar clientes e produtos para seleção
                cursor.execute("SELECT id, nome FROM clientes")
                clientes = cursor.fetchall()
                cursor.execute("SELECT id, nome FROM produtos")
                produtos = cursor.fetchall()
                conn.close()

                # Inputs fora de st.form() para permitir atualização dinâmica
                st.markdown('<label class="form-label" for="cliente"><i class="fa-solid fa-users"></i> Cliente</label>', unsafe_allow_html=True)
                cliente_escolhido = st.selectbox("", clientes, format_func=lambda c: c["nome"], label_visibility="collapsed")

                st.markdown('<label class="form-label" for="produto"><i class="fa-solid fa-shirt"></i> Produto</label>', unsafe_allow_html=True)
                produto_opcao = st.selectbox("", produtos, format_func=lambda p: p["nome"], label_visibility="collapsed")
                produto_id = produto_opcao["id"]

                # Buscar estoque do produto selecionado
                conn = conectar()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT estoque FROM produtos WHERE id = %s", (produto_id,))
                produto_info = cursor.fetchone()
                conn.close()

                estoque_disponivel = produto_info["estoque"]

                st.markdown('<label class="form-label" for="quantidade"><i class="fa-solid fa-bag-shopping"></i> Quantidade comprada</label>', unsafe_allow_html=True)
                quantidade_comprada = st.number_input("", min_value=1, max_value=estoque_disponivel, step=1, label_visibility="collapsed")

                st.markdown('<label class="form-label" for="valor"><i class="fa-solid fa-sack-dollar"></i> Valor da venda (R$)</label>', unsafe_allow_html=True)
                valor = st.number_input("", min_value=0.01, step=0.01, format="%.2f", label_visibility="collapsed")

                st.markdown('<label class="form-label" for="forma"><i class="fa-solid fa-money-check-dollar"></i> Forma de pagamento</label>', unsafe_allow_html=True)
                forma_pagamento = st.selectbox("", ["À vista", "Débito", "Crédito"], label_visibility="collapsed")

                parcelas = None
                if forma_pagamento == "Crédito":
                    parcelas = st.number_input("Número de parcelas", min_value=1, step=1)

                with st.form("form_venda", clear_on_submit=True):

                    submitted = st.form_submit_button("Registrar venda")
                    if submitted:
                        cadastrar_venda(
                        cliente_escolhido["id"],
                        produto_id,
                        valor,
                        forma_pagamento,
                        parcelas,
                        quantidade_comprada
                        )
                        del st.session_state["abrir_cadastro_venda"]
                        st.rerun()

    st.markdown("---")
    st.markdown('<h3 class="listaprodutos"><i class="fa-solid fa-clipboard-list"></i> Lista de Vendas</h3>', unsafe_allow_html=True)

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id, c.nome AS cliente_nome, p.nome AS produto_nome, v.valor, v.forma_pagamento, 
        v.parcelas, v.data_compra, v.quantidade_comprada, v.situacao
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.data_compra DESC
    """)
    vendas = cursor.fetchall()
    conn.close()

    if not vendas:
        st.info("Nenhuma venda cadastrada ainda.")
    else:
        for venda in vendas:
            st.markdown(f'''
            <div class="vendas-card">
                <p class="produto-nome"><i class="fa-solid fa-cart-shopping"></i> Venda {venda['id']} - Cliente: {venda['cliente_nome']}</p>
                <div class="venda-info-container">
                    <p><i class="fa-solid fa-shirt"></i> Produto: {venda['produto_nome']}</p>
                    <p><i class="fa-solid fa-sack-dollar"></i> Valor: {venda['valor']}</p>
                    <p><i class="fa-solid fa-credit-card"></i> Forma de pagamento: {venda['forma_pagamento']}</p>
                    <p><i class="fa-solid fa-calendar"></i> Data da compra: {venda['data_compra']}</p>
                    <p><i class="fa-solid fa-cart-flatbed-suitcase"></i> Quantidade comprada: {venda['quantidade_comprada']}</p>
                    <p><i class="fa-solid fa-folder"></i> Situação: {venda['situacao']}</p>
                </div>
            </div>
    ''', unsafe_allow_html=True)
            #condição fora da string
            if venda['forma_pagamento'] == "Crédito":
                st.markdown(f'''
                <div class="parcela-card">
                    <p><i class="fa-solid fa-credit-card"></i> Parcelas: {venda['parcelas']}</p>
                </div>
            ''', unsafe_allow_html=True)
            
            col_alterar, _, col_deletar, _ = st.columns([1, 0.1, 1, 8])

            with col_alterar:
                if st.button("✏️ Alterar Situação", key=f"alt_status_{venda['id']}"):
                    st.session_state[f"mostrar_update_status_{venda['id']}"] = not st.session_state.get(f"mostrar_update_status_{venda['id']}", False)
                    st.session_state[f"mostrar_delete_venda_{venda['id']}"] = False

            with col_deletar:
                if st.button("🗑️ Deletar", key=f"deletar_venda_{venda['id']}"):
                    st.session_state[f"mostrar_delete_venda_{venda['id']}"] = not st.session_state.get(f"mostrar_delete_venda_{venda['id']}", False)
                    st.session_state[f"mostrar_update_status_{venda['id']}"] = False

            if st.session_state.get(f"mostrar_update_status_{venda['id']}", False):
                with st.form(f"form_status_{venda['id']}"):
                    nova_situacao = st.radio(
                        "Atualizar situação da venda",
                        ["Em aberto", "Pago"],
                        index=0 if venda['situacao'] == "Em aberto" else 1
                    )
                    atualizar_submit = st.form_submit_button("Confirmar atualização")
                    if atualizar_submit:
                        del st.session_state[f"mostrar_update_status_{venda['id']}"]
                        atualizar_status_venda(venda['id'], nova_situacao)

            if st.session_state.get(f"mostrar_delete_venda_{venda['id']}", False):
                with st.form(f"form_deletar_venda_{venda['id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que deseja deletar esta venda? Essa ação não pode ser recuperada.",
                        ("Sim", "Não"),
                        index=1,
                        key=f"confirma_delete_venda_{venda['id']}"
                    )
                    deletar_submit = st.form_submit_button("Confirmar Exclusão")
                    if deletar_submit:
                        if confirmar_delete == "Sim":
                            excluir_venda(venda['id'])
                        elif confirmar_delete == "Não":
                            del st.session_state[f"mostrar_delete_venda_{venda['id']}"]
                            st.rerun()
                        else:
                            st.warning("Selecione uma opção antes de confirmar")
                        
            st.markdown('</div>', unsafe_allow_html=True)