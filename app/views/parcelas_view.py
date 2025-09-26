from mysql.connector import Error
import streamlit as st
from database.connection import conectar
from pathlib import Path

def atualizar_parcelas(fiado_id, nova_qtd, total, venda_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE fiado SET parcelas_pagas = %s WHERE id = %s", (nova_qtd, fiado_id))

    if nova_qtd == total:
        cursor.execute("UPDATE vendas SET situacao = 'Pago' WHERE id = %s", (venda_id,))

    conn.commit()
    conn.close()
    st.success("Parcelas atualizadas com sucesso!")
    st.rerun()

def excluir_parcela(fiado_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fiado WHERE id = %s", (fiado_id,))
    conn.commit()
    conn.close()
    st.warning("Histórico de parcelas excluído com sucesso!")
    st.rerun()

def mostrar_parcela_view():

    style_path = Path(__file__).resolve().parent.parent / "styles" / "fiado_style.css"

    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
""", unsafe_allow_html=True)
    
    st.title("Gerenciamento de Parcelas")
    st.markdown("---")
    st.markdown('<h3 class="listaprodutos"><i class="fa-solid fa-clipboard-list"></i> Lista de Parcelas</h3>', unsafe_allow_html=True)

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            f.id AS fiado_id,
            c.nome AS cliente,
            p.nome AS produto,
            v.valor,
            v.parcelas AS parcelas_total,
            f.parcelas_pagas,
            (v.valor / v.parcelas) AS valor_parcela,
            (f.parcelas_pagas * (v.valor / v.parcelas)) AS valor_pago,
            v.situacao,
            v.data_compra,
            v.id AS venda_id
        FROM fiado f
        JOIN vendas v ON f.venda_id = v.id
        JOIN clientes c ON f.cliente_id = c.id
        JOIN produtos p ON f.produto_id = p.id
        WHERE v.situacao = 'Em aberto'
        ORDER BY v.data_compra DESC
    """)
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        st.info("Nenhuma parcela em aberto encontrada.")
    else:
        for registro in registros:
            st.markdown(f'''
            <div class="parcela-card">
                <p class="parcela-nome"><i class="fa-solid fa-credit-card"></i>Cliente: {registro['cliente']} - Produto: {registro['produto']}</p>
                <div class="parcela-info-container">
                    <p><i class="fa-solid fa-money-check-dollar"></i>Valor total da venda: R$ {registro['valor']:.2f}</p>
                    <p><i class="fa-solid fa-calendar"></i>Data da compra: {registro['data_compra']}</p>
                    <p><i class="fa-solid fa-credit-card"></i>Parcelas totais: {registro['parcelas_total']}</p>
                    <p><i class="fa-solid fa-money-check-dollar"></i>Parcelas pagas: {registro['parcelas_pagas']}</p>
                    <p><i class="fa-solid fa-sack-dollar"></i>Valor de cada parcela: R$ {registro['valor_parcela']:.2f}</p>
                    <p><i class="fa-solid fa-piggy-bank"></i>Valor pago atual: R$ {registro['valor_pago']:.2f}</p>
                    <p><i class="fa-solid fa-folder"></i>Situação: {registro['situacao']}</p>
                </div>
            </div>
    ''', unsafe_allow_html=True)
            
            #botões streamlit
            col_alterar, _, col_deletar, _ = st.columns([1, 0.1, 1, 8])
            with col_alterar:
                if st.button("✏️ Atualizar Parcelas", key=f"update_parcela_{registro['fiado_id']}"):
                    st.session_state[f"atualizar_parcela_{registro['fiado_id']}"] = not st.session_state.get(f"atualizar_parcela_{registro['fiado_id']}")
                    st.session_state[f"confirmar_delete_{registro['fiado_id']}"] = False
            with col_deletar:
                if st.button("🗑️ Excluir Histórico", key=f"delete_parcela_{registro['fiado_id']}"):
                    st.session_state[f"confirmar_delete_{registro['fiado_id']}"] = not st.session_state.get(f"confirmar_delete_{registro['fiado_id']}")
                    st.session_state[f"atualizar_parcela_{registro['fiado_id']}"] = False

            if st.session_state.get(f"atualizar_parcela_{registro['fiado_id']}", False):
                with st.form(f"form_parcelas_{registro['fiado_id']}"):
                    #Gera uma lista de 0 até o total de parcelas
                    opcoes_parcelas = list(range(0, registro['parcelas_total'] + 1))
                    nova_qtd = st.selectbox(
                        "Selecione o novo número de parcelas pagas: ",
                        options= opcoes_parcelas,
                        index=registro['parcelas_pagas']
                    )
                    confirmar = st.radio(
                        "Deseja modificar os dados da parcela?",
                        ("Sim", "Não"),
                        index=0,
                        key=f"confirma_edicao_{registro['fiado_id']}"
                    )
                    submit = st.form_submit_button("Confirmar alteração?")
                    if submit:
                        del st.session_state[f"atualizar_parcela_{registro['fiado_id']}"]
                        if confirmar == "Sim":
                            atualizar_parcelas(
                                fiado_id=registro['fiado_id'],
                                nova_qtd=nova_qtd,
                                total=registro["parcelas_total"],
                                venda_id=registro["venda_id"]
                            )
                        elif confirmar == "Não":
                            st.rerun()
                        else:
                            st.warning("Selecione uma opção antes de confirmar")
            
            if st.session_state.get(f"confirmar_delete_{registro['fiado_id']}", False):
                with st.form(f"form_deletar_{registro['fiado_id']}"):
                    confirmar_delete = st.radio(
                        "Tem certeza que quer deletar o registro de parcela? Essa ação não pode ser recuperada.",
                        ("Sim", "Não"),
                        index=0,
                        key=f"confirma_delete_{registro['fiado_id']}"
                    )
                    deletar_submit = st.form_submit_button("Confirmar Exclusão")
                    if deletar_submit:
                        del st.session_state[f"confirmar_delete_{registro['fiado_id']}"]
                        if confirmar_delete == "Sim":
                            excluir_parcela(registro['fiado_id'])
                        elif confirmar_delete == "Não":
                            st.rerun()
                        else:
                            st.warning("Selecione uma opção antes de confirmar")


            st.markdown('</div>', unsafe_allow_html=True)