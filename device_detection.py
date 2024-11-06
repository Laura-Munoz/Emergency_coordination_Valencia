# utils/device_detection.py
import streamlit as st

def is_mobile():
    """Detecta si es un dispositivo móvil basado en el viewport width"""
    try:
        # Usando JavaScript para obtener el ancho real del dispositivo
        device_width = st.experimental_get_query_params().get('width', ['1200'])[0]
        return int(device_width) < 768
    except:
        return False

def get_viewport_size():
    """Obtiene el tamaño del viewport para debugging"""
    js_code = """
        <script>
            window.parent.document.querySelector('iframe').contentWindow.addEventListener('resize', function() {
                window.streamlit.setComponentValue({
                    width: window.innerWidth,
                    height: window.innerHeight
                });
            });
        </script>
    """
    st.components.v1.html(js_code, height=0)
