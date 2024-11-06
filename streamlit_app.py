# streamlit_app.py
import streamlit as st
import time

# Configuración optimizada para Streamlit Cloud
st.set_page_config(
    page_title="Emergency Valencia",
    page_icon="🚨",
    layout="centered",  # Cambiar a centered para mejor rendimiento móvil
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Optimizaciones para móvil
st.markdown("""
    <style>
    /* Optimizaciones generales */
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    
    /* Optimizaciones móviles */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        
        .stButton > button {
            width: 100%;
            margin: 0.2rem 0;
        }
        
        .stMarkdown {
            font-size: 0.9rem;
        }
        
        /* Ajustar sidebar */
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)



# Cache configuración
st.cache_data.clear()
st.cache_resource.clear()

def main():
    # Añadir manejo de timeout
    try:
        with st.spinner("Cargando..."):
            # Timeout de 10 segundos para carga inicial
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    # Tu código principal aquí
                    break
                except Exception as e:
                    if time.time() - start_time >= 10:
                        st.error("Tiempo de carga excedido. Por favor, recarga la página.")
                        st.stop()
                    time.sleep(0.1)
                    
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()
