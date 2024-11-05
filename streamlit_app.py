# src/app.py
import streamlit as st
from admin_view import admin_page
from coordinator_view import coordinator_page
from volunteer_view import volunteer_page
from database import EmergencyDatabase

# Configuración de Firebase de forma segura
def get_firebase_config():
    try:
        firebase_config = {
            "apiKey": st.secrets["firebase"]["apiKey"],
            "authDomain": st.secrets["firebase"]["authDomain"],
            "databaseURL": st.secrets["firebase"]["databaseURL"],
            "projectId": st.secrets["firebase"]["projectId"],
            "storageBucket": st.secrets["firebase"]["storageBucket"],
            "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
            "appId": st.secrets["firebase"]["appId"]
        }
        return firebase_config
    except Exception as e:
        st.error("Error loading Firebase configuration. Please check your settings.")
        st.stop()

def check_firebase_credentials():
    required_credentials = [
        "apiKey", "authDomain", "databaseURL", 
        "projectId", "storageBucket", "messagingSenderId", "appId"
    ]
    
    for cred in required_credentials:
        if cred not in st.secrets["firebase"]:
            st.error(f"Missing Firebase credential: {cred}")
            st.stop()

# Usa la función al inicio
check_firebase_credentials()

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Emergencias Valencia",
    page_icon="🚨",
    layout="wide"
)

# Inicializar la base de datos
db = EmergencyDatabase()

# Función para limpiar el estado de la sesión
def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Inicializar el estado de la sesión si es necesario
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

# Añadir una clave secreta para acceso admin
ADMIN_SECRET_KEY = "admin123"  # En producción, esto debería estar en un archivo de configuración seguro

# Función para verificar credenciales de admin
def verify_admin(username, password, secret_key):
    return (username == "admin" and 
            password == "admin_password" and  # En producción, usar contraseñas seguras
            secret_key == ADMIN_SECRET_KEY)

# Sidebar para gestión de roles y autenticación
with st.sidebar:
    st.title("🔐 Acceso al Sistema")
    
    if not st.session_state.authenticated:
        # Botón oculto para acceso admin (activado con doble clic o alguna combinación especial)
        if st.session_state.get('show_admin', False):
            if st.button("← Volver"):
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
    # Página de bienvenida cuando no hay rol seleccionado
    st.title("🚨 Sistema de Emergencias Valencia")
    st.write("### Bienvenido al Sistema de Coordinación de Emergencias")
    st.info("""
        👈 Por favor, selecciona tu rol en el panel izquierdo para comenzar:
        
        - 🤝 **Voluntario**: Acceso directo al mapa de zonas
        - 👥 **Coordinador**: Requiere autenticación
        - 🔧 **Administrador**: Requiere autenticación
    """)

# Pie de página
st.markdown("""
    <div style='position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(0, 0, 0, 0.8); 
               padding: 5px; text-align: center; border-top: 1px solid #ddd; font-size: 0.8em;'>
        Develpped by Laura M. Muñoz Amaya | 
        <a href="mailto:lm.munozamay7@gmail.com" style="color: #4A90E2; text-decoration: none;">
            📧 lm.munozamaya7@gmail.com
        </a> | © 2024 
        <br>
        <small style="color: #666;">
            Creado como iniciativa voluntaria para la emergencia de Valencia, España
        </small>
    </div>
    """, unsafe_allow_html=True)
