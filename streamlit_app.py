# streamlit_app.py
import streamlit as st
import platform
import os

# Configuración para mejorar el rendimiento en móvil
os.environ['STREAMLIT_SERVER_PORT'] = "8501"  # Puerto por defecto
os.environ['STREAMLIT_SERVER_ADDRESS'] = "0.0.0.0"  # Permite conexiones externas
os.environ['STREAMLIT_SERVER_HEADLESS'] = "true"  # Modo headless
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = "false"  # Desactiva estadísticas

# Configuración básica
st.set_page_config(
    page_title="Emergency Valencia",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None  # Desactiva menú
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
