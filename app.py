import streamlit as st
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Ficha de Ingreso CIS", page_icon="📋", layout="wide")

# Nombre exacto de tu hoja en Google Drive
NOMBRE_HOJA_GOOGLE = "Base de Datos CIS"

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheets():
    """Conecta con Google Sheets usando los Secretos de Streamlit"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open(NOMBRE_HOJA_GOOGLE).sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
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

# --- INTERFAZ ---
st.title("📋 Registro de Ingreso Social")
st.markdown("---")

# === SECCIÓN 1: DATOS ADMINISTRATIVOS ===
st.subheader("🏢 1. Datos Administrativos")
col1, col2, col3 = st.columns(3)

with col1:
    area = st.selectbox("ÁREA *", ["RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE", "Otro"])
    # Lógica condicional DIPA COMBATE
    gorcis = "NO APLICA"
    if area == "DIPA COMBATE":
        st.info("🔹 Pregunta DIPA COMBATE")
        gorcis = st.radio("¿Requiere evaluación equipo GORCIS?", ["SI", "NO", "NO APLICA"], horizontal=True)
    
    if area == "Otro":
        area_otro = st.text_input("Especifique Área:")
        area = f"Otro: {area_otro}"

with col2:
    prioridad = st.selectbox("PRIORIDAD *", [
        "1. COMUNA 2", "2. COMUNA 14", "3. PERSONA SIN TECHO", 
        "4. ORGAS", "5. GERENCIA", "6. 9 DE JULIO", "7. OTRAS"
    ])

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
    tipo_doc = st.selectbox("TIPO DE DOCUMENTO *", ["DNI", "PASAPORTE", "PRECARIA", "OTRO"])
    dni = st.text_input("NÚMERO DE IDENTIDAD *", placeholder="Ej: 30451327 (Sin puntos)")

with c_p3:
    fecha_nac = st.date_input("FECHA NACIMIENTO", min_value=date(1920, 1, 1))
    edad = calcular_edad(fecha_nac)
    st.write(f"🧮 **Edad:** {edad} años")

c_d1, c_d2 = st.columns(2)
with c_d1:
    doc_ingreso = st.radio("¿TIENE DOC. NECESARIA PARA INGRESO? *", ["SI", "NO"], horizontal=True)
with c_d2:
    foto_dni = st.radio("FOTO DNI/TRÁMITE (Enviada a Wpp) *", ["SI", "NO"], horizontal=True)

st.divider()

# === SECCIÓN 3: SALUD Y MEDICACIÓN ===
st.subheader("cS 3. Salud y Medicación")
c_s1, c_s2, c_s3 = st.columns(3)

with c_s1:
    prob_salud = st.selectbox("PROBLEMÁTICA DE SALUD *", ["NO", "SI"])
    cud = st.selectbox("CUD *", ["NO", "SI", "NO REQUIERE"])

with c_s2:
    autovalidez = st.selectbox("AUTOVALIDEZ *", ["SI", "NO"])
    cama_baja = st.selectbox("SOLICITUD CAMA BAJA *", ["NO", "SI"])

with c_s3:
    escaleras = st.selectbox("APTO SUBIR ESCALERAS *", ["SI", "NO"])

diag_medico = st.text_area("DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO (Especificar motivo cama baja)")

# -- Lógica Medicación --
st.markdown("#### 💊 Detalle Medicación")
toma_med = st.radio("¿TOMA MEDICACIÓN? *", ["NO", "SI"], horizontal=True)

# Variables por defecto
cual_med = "NO APLICA"
esquema = "NO REQUIERE"
posee_med = "NO REQUIERE"
foto_esquema = "NO REQUIERE"

if toma_med == "SI":
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        cual_med = st.text_input("¿CUÁL MEDICACIÓN?")
        posee_med = st.radio("¿POSEE MEDICACIÓN PARA 2 DÍAS?", ["SI", "NO", "NO REQUIERE"], horizontal=True)
    with col_med2:
        esquema = st.radio("¿CUENTA CON ESQUEMA?", ["SI", "NO", "NO REQUIERE"], horizontal=True)
        foto_esquema = st.radio("FOTO DEL ESQUEMA (Enviada Wpp)", ["SI", "NO", "NO REQUIERE"], horizontal=True)

st.divider()

# === SECCIÓN 4: HIGIENE Y MOVILIDAD ===
st.subheader("♿ 4. Higiene y Movilidad")
c_h1, c_h2 = st.columns(2)

with c_h1:
    usa_panales = st.selectbox("¿USA PAÑALES? *", ["NO", "SI"])
    higieniza_solo = "NO USA"
    if usa_panales == "SI":
        higieniza_solo = st.radio("¿PUEDE HIGIENIZARSE SOLO?", ["Sí", "NO"])

with c_h2:
    inst_movilidad = st.selectbox("¿INSTRUMENTO PARA MOVILIDAD? *", ["NO", "SI"])
    cual_inst = "NINGUNO"
    if inst_movilidad == "SI":
        cual_inst = st.selectbox("¿CUÁL UTILIZA?", ["SILLA DE RUEDAS", "BASTON", "ANDADOR", "MULETAS"])
    
    yeso = st.selectbox("¿TIENE YESO O PARTE INMOVILIZADA? *", ["NO", "SI"])

st.divider()

# === SECCIÓN 5: SITUACIÓN SOCIAL ===
st.subheader("🏘️ 5. Situación Social y Laboral")
c_soc1, c_soc2 = st.columns(2)

with c_soc1:
    tiempo_calle = st.selectbox("TIEMPO EN CALLE *", [
        "NO RECUERDA", "MENOS DE 1 MES", "MAS DE 1 MES", 
        "ENTRE 1 Y 6 MESES", "ENTRE 6 MESES Y 1 AÑO", 
        "MAS DE 1 AÑO", "MAS DE 2 AÑOS"
    ])
    motivo_calle = st.selectbox("MOTIVO SIT. CALLE *", [
        "MOTIVO ECONÓMICO", "MOTIVO FAMILIAR", "MOTIVO SALUD", "OTROS MOTIVOS"
    ])
    primera_vez = st.radio("PRIMERA VEZ EN CIS *", ["SI", "NO"], horizontal=True)

with c_soc2:
    sit_laboral = st.selectbox("SITUACIÓN LABORAL *", [
        "Posee empleo", 
        "Desempleado. En búsqueda activa", 
        "Desempleado. Sin búsqueda activa", 
        "Desempleado (Imposibilidad física/mental)"
    ])
    desc_trabajo = "NO APLICA"
    if sit_laboral == "Posee empleo":
        desc_trabajo = st.text_input("DE QUÉ TRABAJA (Rubro, horas, modalidad):")

st.markdown("---")
resumen = st.text_area("📝 DIAGNÓSTICO DEL OPERADOR Y RESUMEN DEL CASO *", height=100)

# === BOTÓN DE GUARDADO ===
# Nota: Al estar fuera de un st.form, este botón envía los datos recolectados arriba
if st.button("🚀 REGISTRAR FICHA EN LA NUBE", type="primary", use_container_width=True):
    
    # Validaciones
    if not nombre or not apellido or not dni:
        st.error("⚠️ Faltan datos obligatorios: Nombre, Apellido o DNI.")
    elif area == "DIPA COMBATE" and gorcis == "NO APLICA": 
         # Pequeña validación extra para DIPA
         st.warning("⚠️ Seleccionó DIPA COMBATE pero no indicó evaluación GORCIS.")
    else:
        with st.spinner("Guardando en Google Drive..."):
            ahora = datetime.now()
            
            # --- LISTA ORDENADA PARA GOOGLE SHEETS ---
            # Este orden debe coincidir EXACTO con las columnas de tu Excel
            fila_datos = [
                ahora.strftime("%d/%m/%Y"), # FECHA REGISTRO
                ahora.strftime("%H:%M"),    # HORA
                area,
                prioridad,
                gorcis,       # Nuevo campo DIPA
                supervisor,
                carta,
                apellido,
                nombre,
                tipo_doc,
                dni,
                fecha_nac.strftime("%d/%m/%Y"),
                edad,
                nacionalidad,
                doc_ingreso,
                foto_dni,
                prob_salud,
                autovalidez,
                cud,
                cama_baja,
                escaleras,
                diag_medico,
                toma_med,
                cual_med,
                esquema,
                posee_med,
                foto_esquema,
                usa_panales,
                higieniza_solo,
                inst_movilidad,
                cual_inst,
                yeso,
                tiempo_calle,
                motivo_calle,
                primera_vez,
                sit_laboral,
                desc_trabajo,
                resumen
            ]
            
            exito = guardar_en_nube(fila_datos)
            
            if exito:
                st.success(f"✅ ¡Ficha de {nombre} {apellido} guardada correctamente!")
                st.balloons()
            else:
                st.error("Hubo un error al conectar con Google Sheets.")
            st.balloons()


