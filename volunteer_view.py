# volunteer_view.py
import streamlit as st
import folium
import time
from database import EmergencyDatabase
from config import CENTER_LAT, CENTER_LON

def create_map(zones):
    """Crea el mapa con las zonas marcadas y una leyenda"""
    if not zones:
        print("No hay zonas para mostrar")
        return ""
    
    m = folium.Map(location=[CENTER_LAT, CENTER_LON], zoom_start=12)
    
    # Agregar leyenda
    legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px;
                    border: 2px solid grey; z-index: 1000;
                    background-color: white;
                    padding: 10px;
                    font-family: Arial;
                    font-size: 14px;">
            <p style="margin: 0; font-weight: bold;">Estado de Zona</p>
            <p style="margin: 5px 0;">
                <i style="background: #008000; border-radius: 50%; display: inline-block; height: 10px; width: 10px;"></i>
                Se necesitan voluntarios
            </p>
            <p style="margin: 5px 0;">
                <i style="background: #FFA500; border-radius: 50%; display: inline-block; height: 10px; width: 10px;"></i>
                Voluntarios óptimos
            </p>
            <p style="margin: 5px 0;">
                <i style="background: #FF0000; border-radius: 50%; display: inline-block; height: 10px; width: 10px;"></i>
                Exceso de voluntarios
            </p>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    for zone in zones:
        try:
            color = {
                'overflow': 'red',
                'needed': '#008000',
                'optimal': 'orange'
            }.get(zone['status'], 'gray')
            
            # Popup simplificado para voluntarios
            popup_text = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0; color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 5px;">
                        {zone['name']}
                    </h4>
                    <div style="margin-top: 10px;">
                        <b style="color: #34495E;">Estado:</b> {zone['status']}<br>
                        <b style="color: #34495E;">Acceso:</b> {zone['access_notes']}<br>
                        <b style="color: #34495E;">Necesidades por cubrir:</b><br>
                        {format_needs(zone.get('pending_needs', []))}<br>
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

def get_cached_data():
    """Obtiene datos con caché agresivo"""
    current_time = time.time()
    cache_time = 60  # 1 minuto de caché
    
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = None
        st.session_state.last_fetch = 0
    
    # Forzar primera carga
    if st.session_state.data_cache is None or (current_time - st.session_state.last_fetch) > cache_time:
        try:
            db = EmergencyDatabase()
            data = db.get_all_zones()
            if data:  # Verificar que hay datos
                st.session_state.data_cache = data
                st.session_state.last_fetch = current_time
            else:
                print("No se obtuvieron datos de la base de datos")
                return []
        except Exception as e:
            print(f"Error obteniendo datos: {e}")
            return []
    
    return st.session_state.data_cache
    
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_map_data():
    try:
        db = EmergencyDatabase()
        return db.get_all_zones()
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return []
        
def volunteer_page():
    st.title("🤝 Mapa - Emergencias Valencia")
    
    # Sidebar con botón de actualización y tiempo
    st.sidebar.write("### Actualización")
    
    with st.sidebar('cargando mapa...'):
        zones = load_map_data()
        
        if st.button("🔄 Actualizar datos"):
            st.session_state.data_cache = None
            st.rerun()
            
        # Mostrar tiempo hasta próxima actualización
        if 'last_fetch' in st.session_state:
            time_remaining = 60 - (time.time() - st.session_state.last_fetch)
            st.sidebar.write(f"Próxima actualización en: {int(time_remaining)} segundos")
    
    # Información para voluntarios
    st.info("""
        👋 ¡Bienvenido, Gracias por tu ayuda!
        
        🎯 Guía de colores:
        - 🟢 Verde: Se necesitan voluntarios en esta zona
        - 🟡 Naranja: Número óptimo de voluntarios
        - 🔴 Rojo: Exceso de voluntarios, considere otras zonas
        
        ℹ️ Haga clic en los marcadores para ver más detalles de cada zona
    """)
    
    # Obtener y mostrar datos
    with st.spinner('Cargando mapa...'):
        zones_data = get_cached_data()
        
        if zones_data:
            # Crear mapa
            map_html = create_map(zones_data)
            # Mostrar mapa usando el componente HTML correcto
            st.components.v1.html(map_html, height=800)
            
            # Contador de zonas que necesitan ayuda
            needed_zones = [z for z in zones_data if z['status'] == 'needed']
            if needed_zones:
                st.warning(f"🚨 Actualmente hay {len(needed_zones)} zonas que necesitan voluntarios")
        else:
            st.error("No se pudieron cargar los datos. Por favor, intenta actualizar la página.")
