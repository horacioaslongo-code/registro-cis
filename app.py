import streamlit as st
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ficha de Ingreso CIS", page_icon="📋", layout="wide")

# Nombre exacto de tu hoja en Google Drive
NOMBRE_HOJA_GOOGLE = "Base de Datos CIS"

# --- FUNCIÓN DE CONEXIÓN CON LIMPIEZA DE CREDENCIALES ---
def conectar_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", 
                 "https://www.googleapis.com/auth/drive"]
        
        # Validación de seguridad
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            st.error("❌ No se encontró [connections.gsheets] en los Secrets.")
            return None
            
        # 1. Extraemos los secretos a un diccionario
        creds_info = st.secrets["connections"]["gsheets"]
        creds_dict = dict(creds_info)
        
        # 2. LIMPIEZA DE LA LLAVE (Evita el Error 200)
        if "private_key" in creds_dict:
            # Quitamos espacios y procesamos saltos de línea
            pk = creds_dict["private_key"].strip().replace("\\n", "\n")
            # Quitamos comillas dobles accidentales si existen
            pk = pk.replace('"', '')
            # Re-añadimos el formato correcto si se dañó al limpiar
            if not pk.startswith("-----BEGIN"):
                st.error("❌ La private_key no tiene el formato correcto.")
                return None
            creds_dict["private_key"] = pk
        
        # 3. Autenticación
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # 4. Apertura del archivo
        sheet = client.open(NOMBRE_HOJA_GOOGLE).sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ Error detallado de conexión: {str(e)}")
        return None

def guardar_en_nube(datos_lista):
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

# --- INTERFAZ DEL FORMULARIO ---
st.title("📋 Registro de Ingreso Social")
st.markdown("---")

# === SECCIÓN 1: DATOS ADMINISTRATIVOS ===
st.subheader("🏢 1. Datos Administrativos")
col1, col2, col3 = st.columns(3)

with col1:
    area = st.selectbox("ÁREA *", ["RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE", "Otro"])
    gorcis = "NO APLICA"
    if area == "DIPA COMBATE":
        gorcis = st.radio("¿Requiere evaluación GORCIS?", ["SI", "NO", "NO APLICA"], horizontal=True)
    if area == "Otro":
        area_otro = st.text_input("Especifique Área:")
        area = f"Otro: {area_otro}"

with col2:
    prioridad = st.selectbox("Prioridad *", ["1. COMUNA 2", "2. COMUNA 14", "3. PERSONA SIN TECHO", "4. ORGAS", "5. GERENCIA", "6. 9 DE JULIO", "7. OTRAS"])

with col3:
    supervisor = st.text_input("SUPERVISOR/A *")
    carta = st.text_input("NÚMERO DE CARTA *")

st.divider()

# === SECCIÓN 2: DATOS PERSONALES ===
st.subheader("👤 2. Datos Personales")
c_p1, c_p2, c_p3 = st.columns(3)

with c_p1:
    apellido = st.text_input("APELLIDO *")
    nombre = st.text_input("NOMBRE *")
    nacionalidad = st.text_input("NACIONALIDAD")

with c_p2:
    dni = st.text_input("NÚMERO DE IDENTIDAD *", help="Sin puntos")
    tipo_doc = st.selectbox("TIPO DE DOCUMENTO *", ["DNI", "PASAPORTE", "PRECARIA", "OTRO"])

with c_p3:
    fecha_nac = st.date_input("FECHA NACIMIENTO", min_value=date(1920, 1, 1))
    edad = calcular_edad(fecha_nac)
    st.write(f"🧮 **Edad:** {edad} años")

col_doc1, col_doc2 = st.columns(2)
with col_doc1:
    doc_ingreso = st.radio("¿TIENE DOC. NECESARIA PARA INGRESO? *", ["SI", "NO"], horizontal=True)
with col_doc2:
    foto_dni = st.radio("FOTO DNI/EXTRAVÍO ENVIADA? *", ["SI", "NO"], horizontal=True)

st.divider()

# === SECCIÓN 3: SALUD Y MEDICACIÓN ===
st.subheader("🏥 3. Salud y Medicación")
c_s1, c_s2, c_s3 = st.columns(3)
with c_s1:
    prob_salud = st.selectbox("PROBLEMÁTICA DE SALUD *", ["NO", "SI"])
    cud = st.selectbox("CUD *", ["SI", "NO", "NO REQUIERE"])
with c_s2:
    autovalidez = st.selectbox("AUTOVALIDEZ *", ["SI", "NO"])
    cama_baja = st.selectbox("SOLICITUD CAMA BAJA *", ["SI", "NO"])
with c_s3:
    escaleras = st.selectbox("APTO ESCALERAS *", ["SI", "NO"])

diag_medico = st.text_area("DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO")

toma_med = st.radio("¿TOMA MEDICACIÓN? *", ["NO", "SI"], horizontal=True)
cual_med, esquema, posee_med, foto_esquema = "NO APLICA", "NO REQUIERE", "NO REQUIERE", "NO REQUIERE"

if toma_med == "SI":
    mc1, mc2 = st.columns(2)
    with mc1:
        cual_med = st.text_input("¿CUÁL MEDICACIÓN?")
        posee_med = st.radio("¿POSEE MEDICACIÓN PARA 2 DÍAS?", ["SI", "NO", "NO REQUIERE"])
    with mc2:
        esquema = st.radio("¿CUENTA CON ESQUEMA?", ["SI", "NO", "NO REQUIERE"])
        foto_esquema = st.radio("FOTO ESQUEMA ENVIADA?", ["SI", "NO", "NO REQUIERE"])

st.divider()

# === SECCIÓN 4: HIGIENE Y MOVILIDAD ===
st.subheader("♿ 4. Higiene y Movilidad")
ch1, ch2 = st.columns(2)
with ch1:
    usa_panales = st.selectbox("¿USA PAÑALES? *", ["SI", "NO"])
    higieniza_solo = "NO USA"
    if usa_panales == "SI":
        higieniza_solo = st.radio("¿PUEDE HIGIENIZARSE SOLO?", ["Sí", "NO"])
with ch2:
    inst_movilidad = st.selectbox("¿INSTRUMENTO MOVILIDAD? *", ["SI", "NO"])
    cual_inst = "NINGUNO"
    if inst_movilidad == "SI":
        cual_inst = st.selectbox("¿CUÁL?", ["SILLA DE RUEDAS", "BASTON", "ANDADOR", "MULETAS"])
    yeso = st.selectbox("¿TIENE YESO? *", ["SI", "NO"])

st.divider()

# === SECCIÓN 5: SOCIAL ===
st.subheader("🏘️ 5. Situación Social")
cs1, cs2 = st.columns(2)
with cs1:
    tiempo_calle = st.selectbox("TIEMPO EN CALLE *", ["NO RECUERDA", "MENOS DE 1 MES", "MAS DE 1 MES", "ENTRE 1 Y 6 MESES", "ENTRE 6 MESES Y 1 AÑO", "MAS DE 1 AÑO", "MAS DE 2 AÑOS"])
    motivo_calle = st.selectbox("MOTIVO SIT. CALLE *", ["MOTIVO ECONÓMICO", "MOTIVO FAMILIAR", "MOTIVO SALUD", "OTROS MOTIVOS"])
    primera_vez = st.radio("PRIMERA VEZ EN CIS *", ["SI", "NO"], horizontal=True)
with cs2:
    sit_laboral = st.selectbox("SITUACIÓN LABORAL *", ["Posee empleo", "Desempleado", "Búsqueda activa", "Imposibilidad salud"])
    desc_trabajo = st.text_input("DE QUÉ TRABAJA/DETALLE *")

resumen = st.text_area("📝 DIAGNÓSTICO DEL OPERADOR *")

# === BOTÓN DE GUARDADO ===
if st.button("🚀 REGISTRAR EN GOOGLE SHEETS", type="primary", use_container_width=True):
    if not (nombre and apellido and dni):
        st.error("⚠️ Falta completar Nombre, Apellido o DNI.")
    else:
        with st.spinner("Guardando..."):
            ahora = datetime.now()
            fila = [
                ahora.strftime("%d/%m/%Y %H:%M:%S"), area, prioridad, supervisor, carta, 
                apellido, nombre, dni, "", tipo_doc, fecha_nac.strftime("%d/%m/%Y"), 
                edad, nacionalidad, foto_dni, prob_salud, autovalidez, cud, cama_baja, 
                escaleras, diag_medico, toma_med, cual_med, esquema, foto_esquema, 
                posee_med, tiempo_calle, motivo_calle, primera_vez, sit_laboral, 
                desc_trabajo, desc_trabajo, resumen, doc_ingreso, usa_panales, 
                higieniza_solo, inst_movilidad, cual_inst, yeso, "", gorcis
            ]
            if guardar_en_nube(fila):
                st.success("✅ ¡Guardado con éxito!")
                st.balloons()
                st.balloons()


