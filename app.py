import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CIS - Sistema Cloud", page_icon="☁️", layout="wide")

# Nombre de tu hoja en Google Drive (Debe coincidir EXACTO)
NOMBRE_HOJA_GOOGLE = "Base de Datos CIS"

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheets():
    """Conecta con Google Sheets usando los Secretos de Streamlit"""
    try:
        # Recuperamos la configuración de los Secrets
        # Streamlit guarda los secretos en st.secrets
        # Necesitamos convertir el objeto de secretos en un diccionario simple para oauth
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Creamos las credenciales desde la información en st.secrets
        # Asumiendo que pegaste el contenido del JSON bajo [connections.gsheets]
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # Limpieza: gspread necesita que 'private_key' tenga los saltos de línea reales (\n)
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja
        sheet = client.open(NOMBRE_HOJA_GOOGLE).sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return None

# --- FUNCIONES ---
def guardar_en_nube(datos_lista):
    """Recibe una lista de datos y la agrega como fila en Sheets"""
    hoja = conectar_sheets()
    if hoja:
        try:
            hoja.append_row(datos_lista)
            return True
        except Exception as e:
            st.error(f"Error escribiendo datos: {e}")
            return False
    return False

def calcular_edad(fecha_nac):
    if not fecha_nac: return 0
    today = date.today()
    return today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))

# --- INTERFAZ ---
st.title("☁️ Registro CIS - Conectado a Drive")
st.info("🟢 Estado: Sistema Online guardando en Google Sheets")

with st.form("entry_form", clear_on_submit=True):
    
    st.markdown("### Datos de Ingreso")
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox("Área", ["RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE"])
        prioridad = st.selectbox("Prioridad", ["1. COMUNA 2", "2. COMUNA 14", "3. SIN TECHO", "OTRAS"])
        supervisor = st.text_input("Supervisor")
        carta = st.text_input("N° Carta")
    
    with col2:
        nombre = st.text_input("Nombre *")
        apellido = st.text_input("Apellido *")
        dni = st.text_input("DNI (Sin puntos) *")
        fecha_nac = st.date_input("Fecha Nacimiento", min_value=date(1950,1,1))
    
    col3, col4 = st.columns(2)
    with col3:
        nacionalidad = st.text_input("Nacionalidad")
        genero = st.selectbox("Género", ["Masc", "Fem", "Otro"])
    with col4:
        tipo_doc = st.selectbox("Tipo Doc", ["DNI", "Pasaporte", "Indoc"])
        
    obs = st.text_area("Observaciones Sociales / Diagnóstico", height=80)
    
    # Botón de envío
    submitted = st.form_submit_button("🚀 REGISTRAR EN LA NUBE", use_container_width=True)

    if submitted:
        if not nombre or not dni:
            st.warning("⚠️ Falta Nombre o DNI")
        else:
            with st.spinner("Guardando en Google Drive..."):
                # Preparar la fila EXACTAMENTE en el orden de las columnas de tu Excel
                edad = calcular_edad(fecha_nac)
                ahora = datetime.now()
                fecha_str = ahora.strftime("%Y-%m-%d")
                hora_str = ahora.strftime("%H:%M:%S")
                
                # LA LISTA MAESTRA (Orden de columnas)
                # Asegúrate que tu Google Sheet tenga estas columnas en este orden
                fila_datos = [
                    fecha_str,  # Columna A
                    hora_str,   # Columna B
                    area,       # Columna C
                    prioridad,  # ...
                    supervisor,
                    carta,
                    nombre,
                    apellido,
                    dni,
                    tipo_doc,
                    nacionalidad,
                    edad,
                    genero,
                    obs
                ]
                
                exito = guardar_en_nube(fila_datos)
                
                if exito:
                    st.success(f"✅ ¡Listo! {nombre} registrado correctamente en la nube.")
                    st.balloons()
            st.toast(f"✅ Ficha de {nombre} guardada correctamente!", icon="🎉")
            st.balloons()

