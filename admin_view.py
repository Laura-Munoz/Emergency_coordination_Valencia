# admin_view.py

import streamlit as st
import folium
from database import EmergencyDatabase
from config import CENTER_LAT, CENTER_LON
from coordinator_view import create_map  # Reutilizamos la función del mapa

def admin_page():
    st.title("🔧 Panel de Administración - Emergencias Valencia")
    
    # Inicializar base de datos
    db = EmergencyDatabase()
    
    # Crear tabs para diferentes funciones administrativas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Vista General", 
        "➕ Añadir Zona", 
        "✏️ Editar Zona", 
        "👥 Gestión Coordinadores",
        "🔄 Mantenimiento"
    ])
    
    # Obtener datos actuales
    if 'zones_data' not in st.session_state:
        st.session_state.zones_data = db.get_all_zones()

    with tab1:
        # Vista del Mapa
        st.subheader("Mapa de Zonas")
        if 'zones_data' not in st.session_state:
            st.session_state.zones_data = db.get_all_zones()
        
        map_html = create_map(st.session_state.zones_data)
        st.components.v1.html(map_html, height=600)
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        col1, col2, col3 = st.columns(3)
        
        zones = st.session_state.zones_data
        with col1:
            st.metric("Total Zonas", len(zones))
        with col2:
            needed_zones = len([z for z in zones if z['status'] == 'needed'])
            st.metric("Zonas Necesitadas", needed_zones)
        with col3:
            overflow_zones = len([z for z in zones if z['status'] == 'overflow'])
            st.metric("Zonas Saturadas", overflow_zones)
    
    with tab2:
        st.subheader("Añadir Nueva Zona")
        with st.form("new_zone_form"):
            name = st.text_input("Nombre de la Zona")
            
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitud", value=CENTER_LAT)
            with col2:
                longitude = st.number_input("Longitud", value=CENTER_LON)
            
            access_notes = st.text_area("Notas de Acceso")
            
            if st.form_submit_button("Crear Zona"):
                new_zone = {
                    'name': name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'volunteer_count': 0,
                    'status': 'needed',
                    'access_notes': access_notes,
                    'pending_needs': [],
                    'covered_needs': []
                }
                
                if db.add_new_zone(new_zone):
                    st.success(f"✅ Zona '{name}' creada exitosamente")
                    st.session_state.zones_data = db.get_all_zones()
                    st.rerun()
    
    with tab3:
        st.subheader("Editar Zona Existente")
        
        # Selector de zona a editar
        selected_zone = st.selectbox(
            "Seleccionar zona a editar",
            options=[zone['name'] for zone in st.session_state.zones_data],
            key="edit_zone_select"
        )
        
        # Encontrar la zona seleccionada
        current_zone = next(
            (zone for zone in st.session_state.zones_data if zone['name'] == selected_zone),
            None
        )
        
        if current_zone:
            with st.form("edit_zone_form"):
                st.write("### Editar Información de la Zona")
                
                new_name = st.text_input("Nombre de la Zona", value=current_zone['name'])
                
                col1, col2 = st.columns(2)
                with col1:
                    new_lat = st.number_input(
                        "Latitud",
                        value=float(current_zone['latitude'])
                    )
                with col2:
                    new_lon = st.number_input(
                        "Longitud",
                        value=float(current_zone['longitude'])
                    )
                
                new_notes = st.text_area(
                    "Notas de Acceso",
                    value=current_zone['access_notes']
                )
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.form_submit_button("Guardar Cambios"):
                        update_data = {
                            'name': new_name,
                            'latitude': new_lat,
                            'longitude': new_lon,
                            'access_notes': new_notes
                        }
                        
                        if db.edit_zone(current_zone['id'], update_data):
                            st.success("✅ Zona actualizada exitosamente")
                            st.session_state.zones_data = db.get_all_zones()
                            st.rerun()
                        else:
                            st.error("❌ Error al actualizar la zona")
                with col4:
                    if st.form_submit_button("🗑️ Eliminar Zona", type="secondary"):
                        # Agregar confirmación
                        if st.session_state.get('confirm_delete', False):
                            if db.delete_zone(current_zone['id']):
                                st.success("✅ Zona eliminada exitosamente")
                                st.session_state.zones_data = db.get_all_zones()
                                del st.session_state['confirm_delete']
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar la zona")
                        else:
                            st.session_state.confirm_delete = True
                            st.warning("⚠️ ¿Estás seguro? Presiona nuevamente para confirmar")
                
    
    with tab5:
        st.subheader("Mantenimiento de Base de Datos")
        
        # Reestructuración de datos
        with st.expander("🔄 Reestructuración de Datos"):
            st.warning("⚠️ Esta acción solo debe realizarse una vez cuando sea necesario reorganizar la base de datos.")
            if st.button("Reestructurar Datos"):
                if db.restructure_firebase_data():
                    st.success("✅ Datos reestructurados correctamente")
                    st.session_state.zones_data = db.get_all_zones()
                    st.rerun()
    with tab4:
        st.subheader("Gestión de Coordinadores")
        
        # Añadir nuevo coordinador
        with st.expander("➕ Añadir Nuevo Coordinador"):
            with st.form("new_coordinator_form"):
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("Usuario")
                with col2:
                    password = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("Registrar Coordinador"):
                    if username and password:
                        success, message = db.add_coordinator(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Por favor complete ambos campos")
        
        # Lista de coordinadores
        st.write("### Coordinadores Registrados")
        coordinators = db.get_all_coordinators()
        
        if coordinators:
            for coord in coordinators:
                with st.expander(f"👤 {coord['username']}"):
                    st.write(f"**Estado:** {'Activo' if coord.get('active', True) else 'Inactivo'}")
                    st.write(f"**Creado:** {coord['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if coord.get('active', True):
                            if st.button("❌ Desactivar", key=f"deact_{coord['username']}"):
                                if db.deactivate_coordinator(coord['username']):
                                    st.success("Coordinador desactivado")
                                    st.rerun()
                                else:
                                    st.error("Error al desactivar coordinador")
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"del_{coord['username']}"):
                            if db.delete_coordinator(coord['username']):
                                st.success("Coordinador eliminado")
                                st.rerun()
                            else:
                                st.error("Error al eliminar coordinador")
        else:
            st.info("No hay coordinadores registrados")