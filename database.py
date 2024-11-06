# src/database.py
# src/database.py
import requests
import json
from datetime import datetime
#from firebase_config import config
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
from config import CENTER_LAT, CENTER_LON, INITIAL_ZONES 

class EmergencyDatabase:
    def __init__(self):
        self.db_url = config['databaseURL']
        
    def initialize_firebase(self):
        if not firebase_admin._apps:
            try:
                credentials_dict = {
                    "type": "service_account",
                    "project_id": st.secrets["firebase"]["project_id"],
                    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
                    "client_email": st.secrets["firebase"]["client_email"],
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
                
                firebase_config = {
                    'databaseURL': st.secrets["firebase"]["databaseURL"]
                }
                
                cred = credentials.Certificate(credentials_dict)
                firebase_admin.initialize_app(cred, firebase_config)
                return True
            except Exception as e:
                st.error(f"Error initializing Firebase: {e}")
                return False
                
    def _make_request(self, method, path, data=None):
        url = f"{self.db_url}/{path}.json"
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, json=data)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error en la solicitud: {e}")
            return None

    def clean_zones_data(self, zones_data):
        """Limpia los datos de las zonas removiendo valores null"""
        if not zones_data:
            return []
        
        if isinstance(zones_data, dict):
            return list(zones_data.values())
        elif isinstance(zones_data, list):
            return [zone for zone in zones_data if zone is not None]
        return []

    def restructure_firebase_data(self):
        """Reestructura los datos en Firebase para usar un diccionario en lugar de un array"""
        try:
            current_data = self._make_request('GET', 'zones')
            
            if not current_data:
                print("No hay datos para reestructurar")
                return False
            
            # Crear nuevo diccionario con las zonas válidas
            new_zones = {}
            for i, zone in enumerate(current_data):
                if zone is not None:
                    zone_id = f"zone_{i}"
                    new_zones[zone_id] = zone
                    # Asegurar que todos los campos necesarios existan
                    new_zones[zone_id].update({
                        'id': zone_id,
                        'pending_needs': zone.get('pending_needs', []),
                        'covered_needs': zone.get('covered_needs', []),
                        'last_update': zone.get('last_update', str(datetime.now()))
                    })
            
            # Actualizar Firebase con la nueva estructura
            result = self._make_request('PUT', 'zones', new_zones)
            return result is not None
            
        except Exception as e:
            print(f"Error en la reestructuración: {e}")
            return False

    def get_all_zones(self):
        """Obtiene todas las zonas de Firebase"""
        try:
            zones_data = self._make_request('GET', 'zones')
            return self.clean_zones_data(zones_data)
        except Exception as e:
            print(f"Error obteniendo zonas: {e}")
            return []

    def update_zone(self, zone_id, data):
        """Actualiza una zona específica"""
        try:
            # Asegurar que las listas existan y sean listas válidas
            pending_needs = data.get('pending_needs', [])
            if pending_needs is None:
                pending_needs = []
                
            covered_needs = data.get('covered_needs', [])
            if covered_needs is None:
                covered_needs = []
            
            # Asegurar que todos los campos necesarios existen
            update_data = {
                'name': data['name'],
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'volunteer_count': data['volunteer_count'],
                'status': data['status'],
                'access_notes': data['access_notes'],
                'pending_needs': list(pending_needs),  # Convertir explícitamente a lista
                'covered_needs': list(covered_needs),  # Convertir explícitamente a lista
                'last_update': str(datetime.now())
            }
            
            # Imprimir para debug
            print("Datos a enviar a Firebase:", update_data)
            
            # Si zone_id no tiene el prefijo 'zone_', añadirlo
            if not zone_id.startswith('zone_'):
                zone_id = f"zone_{zone_id}"
            
            result = self._make_request('PATCH', f'zones/{zone_id}', update_data)
            
            # Verificar resultado
            if result:
                print("Actualización exitosa:", result)
            else:
                print("Error en la actualización")
            
            return result is not None
            
        except Exception as e:
            print(f"Error actualizando zona: {e}")
            return False

    def initialize_zones(self, initial_zones):
        """Inicializa las zonas en Firebase"""
        try:
            zones_data = {}
            for i, zone in enumerate(initial_zones):
                zone_id = f"zone_{i}"
                zone_data = {
                    'name': zone['name'],
                    'latitude': zone['latitude'],
                    'longitude': zone['longitude'],
                    'volunteer_count': zone['volunteer_count'],
                    'status': zone['status'],
                    'access_notes': zone['access_notes'],
                    'pending_needs': zone.get('pending_needs', []),
                    'covered_needs': zone.get('covered_needs', []),
                    'last_update': str(datetime.now()),
                    'id': zone_id
                }
                zones_data[zone_id] = zone_data
            
            result = self._make_request('PUT', 'zones', zones_data)
            return result is not None
        except Exception as e:
            print(f"Error inicializando zonas: {e}")
            return None
    
    #Agregando una zona nueva
    # En database.py, añade este método a la clase EmergencyDatabase:
    def add_new_zone(self, zone_data):
        """Añade una nueva zona a Firebase"""
        try:
            # Obtener zonas actuales
            current_zones = self._make_request('GET', 'zones')
        
            # Si no hay zonas, inicializar como diccionario vacío
            if not current_zones:
                current_zones = {}
                new_id = 0
            else:
                # Calcular el nuevo ID basado en las zonas existentes
                existing_ids = [int(key.split('_')[1]) for key in current_zones.keys() if key.startswith('zone_')]
                new_id = max(existing_ids) + 1 if existing_ids else 0
        
            # Crear ID para la nueva zona
            zone_id = f"zone_{new_id}"
        
            # Asegurar que todos los campos necesarios existan
            new_zone_data = {
                'name': zone_data['name'],
                'latitude': zone_data['latitude'],
                'longitude': zone_data['longitude'],
                'volunteer_count': zone_data.get('volunteer_count', 0),
                'status': zone_data.get('status', 'needed'),
                'access_notes': zone_data.get('access_notes', ''),
                'pending_needs': zone_data.get('pending_needs', []),
                'covered_needs': zone_data.get('covered_needs', []),
                'last_update': str(datetime.now()),
                'id': zone_id
            }
        
            # Hacer la actualización en Firebase
            result = self._make_request('PATCH', f'zones/{zone_id}', new_zone_data)
        
            if result:
                print(f"Zona añadida exitosamente: {zone_id}")
                return True
            return False
        
        except Exception as e:
            print(f"Error añadiendo nueva zona: {e}")
            return False
    # En database.py, añade estos métodos a la clase EmergencyDatabase:
    def delete_zone(self, zone_id):
        """Elimina una zona de Firebase"""
        try:
            # Asegurar que el ID tenga el formato correcto
            if not zone_id.startswith('zone_'):
                zone_id = f"zone_{zone_id}"
        
            # Obtener todas las zonas actuales
            current_zones = self._make_request('GET', 'zones')
        
            if not current_zones:
                print("No hay zonas para eliminar")
                return False
            
            # Verificar que la zona existe
            if zone_id not in current_zones:
                print(f"Zona {zone_id} no encontrada")
                return False
            
            # Eliminar la zona del diccionario
            del current_zones[zone_id]
        
            # Actualizar Firebase con el nuevo conjunto de zonas
            result = self._make_request('PUT', 'zones', current_zones)
        
            if result is not None:
                print(f"Zona {zone_id} eliminada exitosamente")
                return True
            
            return False
        
        except Exception as e:
            print(f"Error eliminando zona: {e}")
            return False  

    def edit_zone(self, zone_id, zone_data):
        """Edita una zona existente en Firebase"""
        try:
            # Asegurar que el ID tenga el formato correcto
            if not zone_id.startswith('zone_'):
                zone_id = f"zone_{zone_id}"
            
            # Obtener datos actuales de la zona
            current_zone = self._make_request('GET', f'zones/{zone_id}')
            if not current_zone:
                print(f"Zona {zone_id} no encontrada")
                return False
            
            # Actualizar solo los campos proporcionados
            updated_zone = {
                'name': zone_data.get('name', current_zone.get('name')),
                'latitude': zone_data.get('latitude', current_zone.get('latitude')),
                'longitude': zone_data.get('longitude', current_zone.get('longitude')),
                'access_notes': zone_data.get('access_notes', current_zone.get('access_notes')),
                'last_update': str(datetime.now())
            }
        
            # Hacer la actualización
            result = self._make_request('PATCH', f'zones/{zone_id}', updated_zone)
            return result is not None
        
        except Exception as e:
            print(f"Error editando zona: {e}")
            return False
    #Añadiendo coordinadores
    def add_coordinator(self, username, password):
        """Añade un nuevo coordinador autorizado"""
        try:
            # Obtener coordinadores actuales
            coordinators = self._make_request('GET', 'coordinators')
        
            if not coordinators:
                coordinators = {}
        
            # Verificar si el usuario ya existe
            if username in coordinators:
                return False, "El nombre de usuario ya existe"
        
            # Crear nuevo coordinador
            import hashlib
            # Hashear la contraseña
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"DEBUG - Contraseña original: {password}")
            print(f"DEBUG - Contraseña hasheada: {hashed_password}")
        
            coordinator_data = {
                'username': username,
                'password': hashed_password,
                'created_at': str(datetime.now()),
                'active': True
            }
        
            # Añadir a Firebase usando el username como key
            result = self._make_request('PATCH', f'coordinators/{username}', coordinator_data)
            
            if result:
                print(f"DEBUG - Coordinador creado: {coordinator_data}")
                return True, "Coordinador añadido exitosamente"
            return False, "Error al añadir coordinador"
        
        except Exception as e:
            return False, f"Error: {str(e)}"

    def verify_coordinator(self, username, password):
        """Verifica las credenciales del coordinador"""
        try:
            # Obtener el coordinador específico
            coordinator = self._make_request('GET', f'coordinators/{username}')
            print(f"DEBUG - Verificando usuario: {username}")
            print(f"DEBUG - Datos encontrados: {coordinator}")
            
            if not coordinator:
                return False, "Usuario no encontrado"
            
            # Hashear la contraseña para comparar
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"DEBUG - Contraseña ingresada hasheada: {hashed_password}")
            print(f"DEBUG - Contraseña almacenada: {coordinator.get('password')}")
            
            if coordinator.get('password') == hashed_password:
                if coordinator.get('active', True):
                    return True, coordinator
                else:
                    return False, "Cuenta desactivada"
            
            return False, "Contraseña incorrecta"
            
        except Exception as e:
            print(f"DEBUG - Error en verificación: {e}")
            return False, f"Error: {str(e)}"
        
    def deactivate_coordinator(self, username):
        """Desactiva un coordinador"""
        try:
            update_data = {'active': False}
            result = self._make_request('PATCH', f'coordinators/{username}', update_data)
            return result is not None
        except Exception as e:
            print(f"Error desactivando coordinador: {e}")
            return False

    def delete_coordinator(self, username):
        """Elimina un coordinador"""
        try:
            result = self._make_request('PUT', f'coordinators/{username}', None)
            return result is None  # Firebase retorna null cuando la eliminación es exitosa
        except Exception as e:
            print(f"Error eliminando coordinador: {e}")
            return False


    def get_all_coordinators(self):
        """Obtiene lista de coordinadores"""
        try:
            coordinators = self._make_request('GET', 'coordinators')
            if coordinators:
                coordinator_list = []
                for username, data in coordinators.items():
                    data['username'] = username  # Añadir el username a los datos
                    coordinator_list.append(data)
                return coordinator_list
            return []
        except Exception as e:
            print(f"Error obteniendo coordinadores: {e}")
            return []

    def deactivate_coordinator(self, coordinator_id):
        """Desactiva un coordinador"""
        try:
            update_data = {'active': False}
            result = self._make_request('PATCH', f'coordinators/{coordinator_id}', update_data)
            return result is not None
        except Exception as e:
            print(f"Error desactivando coordinador: {e}")
            return False
