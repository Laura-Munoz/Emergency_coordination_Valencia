# config.py

# Coordenadas centrales de Valencia
# Estas coordenadas centrarán nuestro mapa en la zona afectada
CENTER_LAT = 39.424540
CENTER_LON = -0.442743

# Configuración de zonas iniciales
# Esta es nuestra "base de datos" inicial con las zonas más críticas
INITIAL_ZONES = [
    {
        'id': 1,
        'name': 'Zona Cero - Paiporta',
        'latitude': 39.4333300,
        'longitude':  -0.4166700,
        'volunteer_count': 0,      # Número actual de voluntarios
        'status': 'overflow',        # Estado: sobresaturado
        'access_notes': 'Acceso principal bloqueado. Usar ruta alternativa por Av. del Mar',
        'last_update':'2024-11-03 00:00:00'
    },
    {
        'id': 2,
        'name': 'Zona A - Catarroja',
        'latitude': 39.404429,
        'longitude': -0.402599,
        'volunteer_count': 0,       # Pocos voluntarios aquí
        'status': 'needed',          # Se necesitan más voluntarios
        'access_notes': 'Acceso por CV-500. Precaución con agua estancada',
        'last_update':'2024-11-03 03:33:33'
    }
]

# Estados posibles para las zonas
# Estos estados determinarán el color en el mapa y las acciones necesarias
ZONE_STATES = [
    'overflow',  # Rojo - Demasiados voluntarios, redirigir
    'needed',    # Verde - Se necesitan voluntarios
    'optimal'    # Amarillo - Número adecuado de voluntarios
]