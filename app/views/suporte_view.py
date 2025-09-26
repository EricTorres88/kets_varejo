import streamlit as st
from pathlib import Path

def suporte_view():
    style_path = Path(__file__).resolve().parent.parent / "styles" / "suporte_style.css"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)

    st.title("Ajuda e suporte")

    st.markdown('''
        <div class="ajuda_div">
            <h1 class="title1">Precisa de ajuda?</h1>
            <p>Clique aqui e baixe o guia breve de como utilizar o sistema:</p>
        </div>
    ''', unsafe_allow_html=True)

    #CAMINHO PARA BAIXAR O PDF
    pdf_patch = Path(__file__).resolve().parent.parent.parent/"docs"/"Ajuda e suporte.pdf"

    if pdf_patch.exists():
        with open(pdf_patch, "rb") as pdf_file:
            st.download_button(
                label = "📥 Baixar Guia do Sistema",
                data=pdf_file,
                file_name="manual.pdf",
                mime="application/pdf"
            )
    
    else:
        st.warning("Guia não disponível")