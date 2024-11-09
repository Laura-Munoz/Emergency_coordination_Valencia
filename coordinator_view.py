# coordinator_view.py

import streamlit as st
import folium
from datetime import datetime
from database import EmergencyDatabase
from config import CENTER_LAT, CENTER_LON

# Lista de necesidades común
COMMON_NEEDS = [
    "Limpieza de calles",
    "Limpieza de viviendas",
    "Medicamentos básicos",
    "Atención médica",
    "Atención psicológica",
    "Agua potable",
    "Alimentos no perecederos",
    "Ropa y mantas",
    "Transporte de suministros",
    "Albergue temporal animales",
    "Productos de higiene"
]

def create_map(zones):
    """Crea el mapa con las zonas marcadas"""
    if not zones:
        print("No hay zonas para mostrar")
        return ""
    
    m = folium.Map(location=[CENTER_LAT, CENTER_LON], zoom_start=12)
    
    for zone in zones:
        try:
            if not all(k in zone for k in ['status', 'latitude', 'longitude', 'name']):
                print(f"Zona con datos incompletos: {zone}")
                continue

            color = {
                'overflow': 'red',
                'needed': '#008000',
                'optimal': 'orange'
            }.get(zone['status'], 'gray')
            
            popup_text = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px; max-width: 300px;">
                    <h4 style="margin: 0; color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 5px;">
                        {zone['name']}
                    </h4>
                    <div style="margin-top: 10px;">
                        <b style="color: #34495E;">Voluntarios:</b> {zone['volunteer_count']}<br>
                        <b style="color: #34495E;">Estado:</b> {zone['status']}<br>
                        <b style="color: #34495E;">Acceso:</b> {zone['access_notes']}<br>
                        <b style="color: #34495E;">Necesidades por cubrir:</b><br>
                        {format_needs(zone.get('pending_needs', []))}<br>
                        <b style="color: #34495E;">Necesidades cubiertas:</b><br>
                        {format_needs(zone.get('covered_needs', []))}<br>
                        <small style="color: #7F8C8D;">Última actualización: {zone.get('last_update', 'N/A')}</small>
                    </div>
                </div>
            """
            
            marker = folium.CircleMarker(
                location=[zone['latitude'], zone['longitude']],
                radius=15,
                color=color,
                fill=True,
                popup=popup_text
            )
            marker.add_to(m)
        except Exception as e:
            print(f"Error procesando zona: {e}")
    
    return m._repr_html_()

def format_needs(needs):
    """Formatea la lista de necesidades para el popup"""
    if not needs:
        return "Ninguna registrada"
    return "<br>".join(f"- {need}" for need in needs)

def coordinator_page():
    st.title("🚨 Coordinador de Emergencias Valencia")
    
    try:
        # Inicializar base de datos
        db = EmergencyDatabase()
        
        # Obtener datos actuales
        if 'zones_data' not in st.session_state:
            st.session_state.zones_data = db.get_all_zones()

        # En dispositivos móviles, el mapa será más pequeño
        screen_width = st.session_state.get('browser_width', 1000)
        is_mobile = screen_width < 768
        map_height = 400 if is_mobile else 500

        # Contenedor para el mapa
        map_container = st.container()
        with map_container:
            st.subheader("Mapa de Zonas")
            map_html = create_map(st.session_state.zones_data)
            st.components.v1.html(map_html, height=map_height)

        # Contenedor para el panel de control
        control_container = st.container()
        with control_container:
            st.subheader("Panel de Control")
            
            # Si hay datos de zonas
            if st.session_state.zones_data:
                col1, col2 = st.columns([3, 1])  # Hacer el selector de zona más ancho
                with col1:
                    selected_zone = st.selectbox(
                        "Seleccionar Zona",
                        options=[zone['name'] for zone in st.session_state.zones_data]
                    )
                
                current_zone = next(
                    (zone for zone in st.session_state.zones_data if zone['name'] == selected_zone),
                    None
                )
                
                if current_zone:
                    with st.form("update_form", clear_on_submit=True):
                        # Usar 3 columnas para los inputs básicos
                        col1, col2, col3 = st.columns([2, 2, 3])
                        
                        with col1:
                            new_count = st.number_input(
                                "Número de Voluntarios",
                                min_value=0,
                                value=current_zone['volunteer_count']
                            )
                        
                        with col2:
                            new_notes = st.text_area(
                                "Notas de Acceso",
                                value=current_zone['access_notes'],
                                height=100
                            )
                        
                        # Sección de necesidades
                        with col3:
                            st.write("### Necesidades")
                            tab1, tab2 = st.tabs(["Por cubrir", "Cubiertas"])
                            
                            with tab1:
                                pending_needs = current_zone.get('pending_needs', [])
                                new_pending_needs = st.multiselect(
                                    "Seleccionar necesidades pendientes",
                                    options=COMMON_NEEDS,
                                    default=pending_needs if pending_needs else [],
                                    key="pending_needs"
                                )
                            
                            with tab2:
                                covered_needs = current_zone.get('covered_needs', [])
                                new_covered_needs = st.multiselect(
                                    "Seleccionar necesidades cubiertas",
                                    options=COMMON_NEEDS,
                                    default=covered_needs if covered_needs else [],
                                    key="covered_needs"
                                )
                        
                        # Centrar el botón de actualizar
                        submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 1])
                        with submit_col2:
                            if st.form_submit_button("Actualizar", use_container_width=True):
                                if new_count > 150:
                                    new_status = 'overflow'
                                elif new_count < 50:
                                    new_status = 'needed'
                                else:
                                    new_status = 'optimal'
                                
                                update_data = {
                                    'name': current_zone['name'],
                                    'latitude': current_zone['latitude'],
                                    'longitude': current_zone['longitude'],
                                    'volunteer_count': new_count,
                                    'status': new_status,
                                    'access_notes': new_notes,
                                    'pending_needs': new_pending_needs,
                                    'covered_needs': new_covered_needs
                                }
                                
                                if db.update_zone(current_zone['id'], update_data):
                                    st.session_state.zones_data = db.get_all_zones()
                                    st.success(f"Zona {selected_zone} actualizada!")
                                    st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Por favor, verifica la configuración de la base de datos y vuelve a intentar.")
