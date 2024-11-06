# streamlit_app.py
import streamlit as st
import time
from datetime import datetime
from admin_view import admin_page
from coordinator_view import coordinator_page
from volunteer_view import volunteer_page
from database import EmergencyDatabase
from config import CENTER_LAT, CENTER_LON, INITIAL_ZONES

# Limpiar cache al inicio
st.cache_data.clear()
st.cache_resource.clear()

# Configuración optimizada para Streamlit Cloud
st.set_page_config(
   page_title="Sistema de Emergencias Valencia",
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

       /* Optimizar footer en móvil */
       .footer {
           font-size: 10px;
           padding: 3px;
       }
   }
   </style>
""", unsafe_allow_html=True)

# Función para verificar credenciales de admin
def verify_admin(username, password, secret_key):
   return (username == "admin" and 
           password == "admin_password" and
           secret_key == ADMIN_SECRET_KEY)

def main():
   try:
       with st.spinner("Cargando..."):
           # Timeout de 10 segundos para carga inicial
           start_time = time.time()
           
           # Inicializar la base de datos con timeout
           try:
               db = EmergencyDatabase()
               st.success("Conectado exitosamente")
           except Exception as e:
               if time.time() - start_time >= 10:
                   st.error("Tiempo de conexión excedido. Por favor, recarga la página.")
                   st.stop()
               st.error(f"Error en la conexión: {str(e)}")
               st.stop()
           
           # Inicializar el estado de la sesión si es necesario
           if 'authenticated' not in st.session_state:
               st.session_state.authenticated = False
               st.session_state.role = None

           # Añadir una clave secreta para acceso admin
           global ADMIN_SECRET_KEY
           ADMIN_SECRET_KEY = "admin123"

           # Sidebar para gestión de roles y autenticación
           with st.sidebar:
               st.title("🔐 Acceso al Sistema")
               
               if not st.session_state.authenticated:
                   # Botón oculto para acceso admin
                   if st.session_state.get('show_admin', False):
                       if st.button("← Volver", key='back_button'):
                           st.session_state.show_admin = False
                           st.rerun()
                       
                       st.write("🔒 Acceso Administrativo")
                       with st.form("admin_login"):
                           admin_user = st.text_input("Usuario")
                           admin_pass = st.text_input("Contraseña", type="password")
                           admin_key = st.text_input("Clave de Seguridad", type="password")
                           if st.form_submit_button("Ingresar"):
                               if verify_admin(admin_user, admin_pass, admin_key):
                                   st.session_state.authenticated = True
                                   st.session_state.role = "Administrador"
                                   st.rerun()
                               else:
                                   st.error("Credenciales incorrectas")
                   
                   else:
                       # Selector normal para usuarios regulares
                       role_selection = st.radio(
                           "Seleccionar Rol",
                           ["Voluntario", "Coordinador"]
                       )
                       
                       # Botón oculto para mostrar acceso admin
                       col1, col2, col3 = st.columns([1,1,1])
                       with col3:
                           if st.button("⚙️", key="admin_access"):
                               st.session_state.show_admin = True
                               st.rerun()
                       
                       if role_selection == "Voluntario":
                           if st.button("Acceder como Voluntario"):
                               st.session_state.authenticated = True
                               st.session_state.role = "Voluntario"
                               st.rerun()
                               
                       elif role_selection == "Coordinador":
                           st.write("Ingreso como Coordinador")
                           username = st.text_input("Usuario", key="coord_user")
                           password = st.text_input("Contraseña", type="password", key="coord_pass")
                           if st.button("Ingresar", key="coord_submit"):
                               try:
                                   success, result = db.verify_coordinator(username, password)
                                   if success:
                                       st.session_state.authenticated = True
                                       st.session_state.role = role_selection
                                       st.session_state.user_info = result
                                       st.rerun()
                                   else:
                                       st.error(result)
                               except Exception as e:
                                   st.error(f"Error en la verificación: {str(e)}")
               
               else:
                   st.success(f"Rol actual: {st.session_state.role}")
                   if st.button("Cerrar Sesión"):
                       for key in list(st.session_state.keys()):
                           del st.session_state[key]
                       st.rerun()

           # Mostrar la vista correspondiente según el rol
           if st.session_state.authenticated:
               if st.session_state.role == "Administrador":
                   admin_page()
               elif st.session_state.role == "Coordinador":
                   coordinator_page()
               elif st.session_state.role == "Voluntario":
                   volunteer_page()
           else:
               # Página de bienvenida
               st.title("🚨 Sistema de Emergencias Valencia")
               st.write("### Bienvenido al Sistema de Coordinación de Emergencias")
               st.info("""
                   👈 Por favor, selecciona tu rol en el panel izquierdo para comenzar:
                   
                   - 🤝 **Voluntario**: Acceso directo al mapa de zonas
                   - 👥 **Coordinador**: Requiere autenticación
                   - 🔧 **Administrador**: Requiere autenticación
               """)

   except Exception as e:
       st.error(f"Error en la aplicación: {str(e)}")
       st.stop()

if __name__ == "__main__":
   main()

# Footer optimizado
st.markdown("""
   <div class="footer" style="position: fixed; bottom: 0; left: 0; width: 100%; 
        background-color: rgba(0,0,0,0.8); padding: 5px; text-align: center; color: white;">
       Developed by Laura M. Muñoz Amaya | 📧 lm.munozamaya7@gmail.com | © 2024
   </div>
""", unsafe_allow_html=True)

