from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

#Função para cadastrar produtos
def cadastrar_produto(nome, codigo, tamanho, preco, estoque):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, codigo, tamanho, preco, estoque) VALUES (%s, %s, %s, %s, %s)", (nome, codigo, tamanho, preco, estoque))
    conn.commit()
    conn.close()
    st.success("Produto cadastrado com sucesso!")

# Função para atualizar um produto
def atualizar_produto(produto_id, novo_nome, novo_cod, novo_tamanho, novo_preco, novo_estoque):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos
        SET nome = %s, codigo = %s, tamanho = %s, preco = %s, estoque = %s
        WHERE id = %s
    """, (novo_nome, novo_cod, novo_tamanho, novo_preco, novo_estoque, produto_id ))
    conn.commit()
    conn.close()
    st.success("Produto atualizado com sucesso!")
    st.rerun()

# Função para deletar um produto
def deletar_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
    conn.commit()
    conn.close()
    st.warning("Produto deletado com sucesso!")
    st.rerun()

#Função principal

def mostrar_produtos_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "produtos_style.css"

    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    st.title("Cadastro e Gerenciamento de Produtos")
    if st.button("➕ Cadastrar novo produto", key="botao_cadastro"):
        st.session_state["abrir_cadastro"] = not st.session_state.get("abrir_cadastro", False)

    if st.session_state.get("abrir_cadastro", False):
        with st.expander("📋 Formulário de Cadastro", expanded=True):
            with st.form("form_cadastro", clear_on_submit=True):
                st.markdown('<label class="form-label" for="nome"><i class="fa-solid fa-tags"></i> Nome</label>', unsafe_allow_html=True)
                nome = st.text_input("", key="nome_cadastro", placeholder="Ex: Camiseta Adidas Masculina Branca", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="codigo"><i class="fa-solid fa-qrcode"></i> Código</label>', unsafe_allow_html=True)
                codigo = st.text_input("", key="cod_cadastro", placeholder="Ex: XHN008F6", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="tamanho"><i class="fa-solid fa-up-right-and-down-left-from-center"></i> Tamanho</label>', unsafe_allow_html=True)
                tamanho = st.text_input("", key="tamanho_cadastro", placeholder="Ex: 'P', '36'...", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="preco"><i class="fa-solid fa-money-check-dollar"></i> Preço</label>', unsafe_allow_html=True)
                preco = st.number_input("", key="preco_cadastro", min_value=0.01, step=0.01, format="%.2f", label_visibility="collapsed")
                st.markdown('<label class="form-label" for="estoque"><i class="fa-solid fa-dolly"></i> Estoque</label>', unsafe_allow_html=True)
                estoque = st.number_input("", key="estoque_cadastro", min_value=0, step=1, label_visibility="collapsed")
                submitted = st.form_submit_button("Cadastrar")    

            if submitted:
                if preco <= 0:
                    st.warning("O preço não pode ser negativo ou 0.")
                elif estoque < 0:
                    st.warning("O estoque não pode ser negativo.")
                elif nome and codigo and tamanho and preco and estoque:
                    cadastrar_produto(nome, codigo, tamanho, preco, estoque)
                    del st.session_state["abrir_cadastro"]
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos.")

    st.markdown("---")
    st.markdown('<h3 class="listaprodutos"><i class="fa-solid fa-clipboard-list"></i> Lista de Produtos</h3>', unsafe_allow_html=True)

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()

    if not produtos:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        for produto in produtos:
            st.markdown(f'''
            <div class="produto-card">
                <p class="produto-nome"><i class="fa-solid fa-tags"></i> {produto["nome"]}</p>
                <div class="produto-info-container">
                    <p><i class="fa-solid fa-qrcode"></i> Código: {produto["codigo"]}</p>
                    <p><i class="fa-solid fa-up-right-and-down-left-from-center"></i> Tamanho: {produto["tamanho"]}</p>
                    <p><i class="fa-solid fa-money-check-dollar"></i> Preço: {produto["preco"]}</p>
                    <p><i class="fa-solid fa-dolly"></i> Quantidade em estoque: {produto["estoque"]}</p>
                </div>
            </div>
    ''', unsafe_allow_html=True)
            
            # Botões do Streamlit
            col_alterar, _, col_deletar, _ = st.columns([1, 0.1, 1, 8])
            with col_alterar:
                if st.button("✏️ Alterar", key=f"editar_btn_{produto['id']}"):
                    st.session_state[f"mostrar_edicao_{produto['id']}"] = not st.session_state.get(f"mostrar_edicao_{produto['id']}", False)
                    st.session_state[f"mostrar_delete_{produto['id']}"] = False
            with col_deletar:
                if st.button("🗑️ Deletar", key=f"deletar_btn_{produto['id']}"):
                    st.session_state[f"mostrar_delete_{produto['id']}"] = not st.session_state.get(f"mostrar_delete_{produto['id']}", False)
                    st.session_state[f"mostrar_edicao_{produto['id']}"] = False

            if st.session_state.get(f"mostrar_edicao_{produto['id']}", False):
                with st.expander(f"✏️ Alterar dados de {produto['nome']}", expanded=True):
                    st.markdown('<label class="form-label" for="nome"><i class="fa-solid fa-tags"></i> Novo nome</label>', unsafe_allow_html=True)
                    novo_nome = st.text_input("", key=f"nome_{produto['id']}", placeholder="Ex: Camiseta Adidas Masculina Branca", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="codigo"><i class="fa-solid fa-qrcode"></i> Novo código</label>', unsafe_allow_html=True)
                    novo_codigo = st.text_input("", key=f"cod_{produto['codigo']}", placeholder="Ex: XHN008F6", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="tamanho"><i class="fa-solid fa-up-right-and-down-left-from-center"></i> Novo tamanho</label>', unsafe_allow_html=True)
                    novo_tamanho = st.text_input("", key=f"tamanho_{produto['tamanho']}", placeholder="Ex: 'P', '36'...", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="preco"><i class="fa-solid fa-money-check-dollar"></i> Novo preço</label>', unsafe_allow_html=True)
                    novo_preco = st.number_input("", key=f"preco_{produto['preco']}", min_value=0.01, step=0.01, format="%.2f", label_visibility="collapsed")
                    st.markdown('<label class="form-label" for="estoque"><i class="fa-solid fa-dolly"></i> Novo estoque</label>', unsafe_allow_html=True)
                    novo_estoque = st.number_input("", key=f"estoque_{produto['estoque']}", min_value=0, step=1, label_visibility="collapsed")
                    with st.form(f"form_editar_{produto['id']}"):
                        confirmar = st.radio(
                            "Deseja realmente modificar os dados do produto?",
                            ("Sim", "Não"),
                            index = 0,
                            key=f"confirma_edicao_{produto['id']}"
                        )
                        confirmar_submit = st.form_submit_button("Confirmar Alteração")
                        if confirmar_submit:
                            del st.session_state[f"mostrar_edicao_{produto['id']}"]
                            if confirmar == "Sim":
                                if novo_nome.strip() and novo_codigo.strip() and novo_tamanho.strip() and novo_preco > 0 and novo_estoque >= 0:
                                    atualizar_produto(produto['id'], novo_nome, novo_codigo, novo_tamanho, novo_preco, novo_estoque)
                                else:
                                    st.warning("Todos os campos são obrigatórios!")
                            elif confirmar == "Não":
                                st.rerun()
                            else:
                                st.warning("Selecione uma opção antes de confirmar")

            if st.session_state.get(f"mostrar_delete_{produto['id']}", False):
                with st.form(f"form_deletar_{produto['id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que deseja deletar o produto? Esses dados não poderão ser recuperados.",
                        ("Sim", "Não"),
                        index=0,
                        key= f"confirma_delete_{produto['id']}"
                    )
                    deletar_submit = st.form_submit_button("Confirmar Exclusão")
                    if deletar_submit:
                        del st.session_state[f"mostrar_delete_{produto['id']}"]
                        if confirmar_delete == "Sim":
                            deletar_produto(produto['id'])
                        elif confirmar_delete == "Não":
                            st.rerun()
                        else:
                                st.warning("Selecione uma opção antes de confirmar")
            
            st.markdown('</div>', unsafe_allow_html=True)