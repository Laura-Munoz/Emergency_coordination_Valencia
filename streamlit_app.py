import streamlit as st
import time
import sys
import platform

st.write("Python version:", sys.version)
st.write("Platform:", platform.platform())
st.write("Streamlit version:", st.__version__)
# Limpiar cache completamente al inicio
for key in st.session_state.keys():
    del st.session_state[key]
st.cache_data.clear()
st.cache_resource.clear()

# Configuración extremadamente básica
st.set_page_config(
    page_title="Emergency Valencia",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Optimizaciones críticas para móvil
st.markdown("""
    <style>
    /* Desactivar animaciones y transiciones */
    * {
        animation: none !important;
        transition: none !important;
    }
    
    /* Optimizaciones de rendimiento */
    .stApp {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Reducir tamaño de fuentes */
    .stMarkdown {
        font-size: 14px !important;
    }
    
    /* Optimizar botones */
    .stButton > button {
        padding: 0.2rem 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    try:
        # Control de tiempo de carga
        start_time = time.time()
        
        # Contenido mínimo
        st.write("## Sistema de Emergencias")
        
        # Test de interacción básica
        if st.button("Probar Conexión"):
            st.success("Conexión exitosa")
        
        # Monitorear tiempo de carga
        if time.time() - start_time > 5:  # 5 segundos máximo
            st.error("Tiempo de carga excedido")
            st.stop()
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()
