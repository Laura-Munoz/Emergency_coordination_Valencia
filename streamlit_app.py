# streamlit_app.py
import streamlit as st

# Configuración mínima
st.set_page_config(
    page_title="Emergency Valencia",
    page_icon="🚨",
    layout="centered",  # Cambiamos a centered para reducir complejidad
    initial_sidebar_state="collapsed"
)

def main():
    try:
        # Prueba básica de carga
        st.write("Probando carga inicial...")
        
        # Solo mostrar un botón simple
        if st.button("Click para probar"):
            st.success("¡Funcionó!")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
