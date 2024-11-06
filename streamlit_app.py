import streamlit as st

# Configuración mínima
st.set_page_config(
    page_title="Test Emergency",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def main():
    try:
        st.write("# Test de carga")
        st.write("Si puedes ver esto, la app está cargando correctamente")
        
        if st.button("Prueba"):
            st.success("¡El botón funciona!")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
