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
    
    # Inicializar base de datos
    db = EmergencyDatabase()
    
    # Obtener datos actuales
    if 'zones_data' not in st.session_state:
        st.session_state.zones_data = db.get_all_zones()

    # En dispositivos móviles, el layout será vertical
    # En desktop, será horizontal con proporción 40-60
    screen_width = st.session_state.get('browser_width', 1000)
    is_mobile = screen_width < 768

    if is_mobile:
        # Vista móvil: elementos apilados verticalmente
        st.subheader("Mapa de Zonas")
        map_html = create_map(st.session_state.zones_data)
        st.components.v1.html(map_html, height=400)  # Altura reducida para móvil
        
        st.subheader("Panel de Control")
        render_control_panel(st.session_state.zones_data, db, is_mobile)
    else:
        # Vista desktop: usar dos columnas lado a lado sin espacio extra
        left_col, right_col = st.columns([4, 6])
        
        with left_col:
            st.subheader("Mapa de Zonas")
            map_container = st.container()
            with map_container:
                map_html = create_map(st.session_state.zones_data)
                # Ajustar la altura del mapa para que ocupe todo el alto disponible
                st.components.v1.html(map_html, height=800)
        
        with right_col:
            st.subheader("Panel de Control")
            render_control_panel(st.session_state.zones_data, db, is_mobile)

def render_control_panel(zones_data, db, is_mobile):
    """Renderiza el panel de control"""
    if zones_data:
        selected_zone = st.selectbox(
            "Seleccionar Zona",
            options=[zone['name'] for zone in zones_data]
        )
        
        current_zone = next(
            (zone for zone in zones_data if zone['name'] == selected_zone),
            None
        )
        
        if current_zone:
            with st.form("update_form"):
                st.write("### Actualizar Estado")
                
                # En móvil, los campos van uno debajo del otro
                if is_mobile:
                    new_count = st.number_input(
                        "Número de Voluntarios",
                        min_value=0,
                        value=current_zone['volunteer_count']
                    )
                    
                    new_notes = st.text_area(
                        "Notas de Acceso",
                        value=current_zone['access_notes'],
                        height=100
                    )
                    
                    st.write("### Necesidades")
                    st.write("**Por cubrir:**")
                    pending_needs = current_zone.get('pending_needs', [])
                    new_pending_needs = st.multiselect(
                        "Seleccionar necesidades pendientes",
                        options=COMMON_NEEDS,
                        default=pending_needs if pending_needs else [],
                        key="pending_needs"
                    )
                    
                    st.write("**Cubiertas:**")
                    covered_needs = current_zone.get('covered_needs', [])
                    new_covered_needs = st.multiselect(
                        "Seleccionar necesidades cubiertas",
                        options=COMMON_NEEDS,
                        default=covered_needs if covered_needs else [],
                        key="covered_needs"
                    )
                else:
                    # Vista desktop: usar columnas para mejor organización
                    basic_col1, basic_col2 = st.columns(2)
                    with basic_col1:
                        new_count = st.number_input(
                            "Número de Voluntarios",
                            min_value=0,
                            value=current_zone['volunteer_count']
                        )
                    
                    with basic_col2:
                        new_notes = st.text_area(
                            "Notas de Acceso",
                            value=current_zone['access_notes'],
                            height=100
                        )
                    
                    st.write("### Necesidades")
                    needs_col1, needs_col2 = st.columns(2)
                    
                    with needs_col1:
                        st.write("**Por cubrir:**")
                        pending_needs = current_zone.get('pending_needs', [])
                        new_pending_needs = st.multiselect(
                            "Seleccionar necesidades pendientes",
                            options=COMMON_NEEDS,
                            default=pending_needs if pending_needs else [],
                            key="pending_needs"
                        )
                    
                    with needs_col2:
                        st.write("**Cubiertas:**")
                        covered_needs = current_zone.get('covered_needs', [])
                        new_covered_needs = st.multiselect(
                            "Seleccionar necesidades cubiertas",
                            options=COMMON_NEEDS,
                            default=covered_needs if covered_needs else [],
                            key="covered_needs"
                        )
                
                # Botón de actualizar centrado
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
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
