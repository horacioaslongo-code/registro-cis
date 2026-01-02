import streamlit as st
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Ficha de Ingreso CIS", page_icon="📋", layout="wide")
NOMBRE_HOJA_GOOGLE = "Base de Datos CIS"

def conectar_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["connections"]["gsheets"]
        creds_dict = dict(creds_info)
        if "private_key" in creds_dict:
            pk = creds_dict["private_key"].strip().replace("\\n", "\n").replace('"', '')
            creds_dict["private_key"] = pk
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(NOMBRE_HOJA_GOOGLE).sheet1
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

# --- INTERFAZ (Igual a la anterior para no marearte) ---
st.title("📋 Registro de Ingreso Social")
col1, col2, col3 = st.columns(3)
with col1:
    area = st.selectbox("ÁREA *", ["RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE", "Otro"])
    gorcis = "NO APLICA"
    if area == "DIPA COMBATE": gorcis = st.radio("¿Requiere GORCIS?", ["SI", "NO", "NO APLICA"])
with col2:
    prioridad = st.selectbox("Prioridad *", ["1. COMUNA 2", "2. COMUNA 14", "3. PERSONA SIN TECHO", "4. ORGAS", "5. GERENCIA", "6. 9 DE JULIO", "7. OTRAS"])
with col3:
    supervisor = st.text_input("SUPERVISOR/A *")
    carta = st.text_input("NÚMERO DE CARTA *")

st.divider()
c_p1, c_p2, c_p3 = st.columns(3)
with c_p1:
    apellido = st.text_input("APELLIDO *")
    nombre = st.text_input("NOMBRE *")
with c_p2:
    dni = st.text_input("NÚMERO DE IDENTIDAD *")
    tipo_doc = st.selectbox("TIPO DE DOCUMENTO *", ["DNI", "PASAPORTE", "PRECARIA", "OTRO"])
with c_p3:
    fecha_nac = st.date_input("FECHA NACIMIENTO", min_value=date(1920, 1, 1))
    nacionalidad = st.text_input("NACIONALIDAD")
    edad = date.today().year - fecha_nac.year

st.divider()
# ... (Salud y Medicación - Simplificado para el ejemplo de guardado)
prob_salud = st.selectbox("PROBLEMÁTICA DE SALUD", ["NO", "SI"])
autovalidez = st.selectbox("AUTOVALIDEZ", ["SI", "NO"])
cud = st.selectbox("CUD", ["SI", "NO", "NO REQUIERE"])
cama_baja = st.selectbox("SOLICITUD CAMA BAJA", ["SI", "NO"])
escaleras = st.selectbox("APTO ESCALERAS", ["SI", "NO"])
diag_medico = st.text_area("DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO")
toma_med = st.radio("¿TOMA MEDICACIÓN?", ["NO", "SI"])
cual_med = st.text_input("¿CUÁL?") if toma_med == "SI" else "NO APLICA"
esquema = st.radio("CUENTA CON ESQUEMA", ["SI", "NO", "NO REQUIERE"])
foto_esquema = st.radio("FOTO ESQUEMA ENVIADA", ["SI", "NO", "NO REQUIERE"])
posee_med = st.radio("MEDICACIÓN PARA 2 DÍAS", ["SI", "NO", "NO REQUIERE"])

st.divider()
tiempo_calle = st.selectbox("TIEMPO EN CALLE", ["MENOS DE 1 MES", "MAS DE 1 MES", "OTRO"])
motivo_calle = st.selectbox("MOTIVO SIT. CALLE", ["ECONÓMICO", "FAMILIAR", "SALUD", "OTROS"])
primera_vez = st.radio("PRIMERA VEZ EN CIS", ["SI", "NO"])
sit_laboral = st.selectbox("SITUACIÓN LABORAL", ["Posee empleo", "Desempleado", "Búsqueda activa"])
desc_trabajo = st.text_input("DE QUÉ TRABAJA/DETALLE")
resumen = st.text_area("DIAGNÓSTICO DEL OPERADOR")
doc_ingreso = st.radio("¿TIENE DOC. NECESARIA?", ["SI", "NO"])
panales = st.selectbox("¿USA PAÑALES?", ["SI", "NO"])
higieniza = st.radio("¿SE HIGIENIZA SOLO?", ["SI", "NO", "NO USA"])
inst_mov = st.selectbox("¿INSTRUMENTO MOVILIDAD?", ["SI", "NO"])
cual_inst = st.text_input("¿CUÁL?")
yeso = st.selectbox("¿TIENE YESO?", ["SI", "NO"])
foto_dni = st.radio("FOTO DNI ENVIADA", ["SI", "NO"])

# === EL ORDEN DE LOS DATOS (SIGUIENDO TU LISTA) ===
if st.button("🚀 REGISTRAR"):
    ahora = datetime.now()
    # Esta lista debe ser idéntica a tus 40 columnas
    fila = [
        ahora.strftime("%d/%m/%Y %H:%M:%S"), # 1. Marca temporal
        area,                                # 2. ÁREA
        prioridad,                           # 3. Prioridad
        supervisor,                          # 4. SUPERVISOR/A
        carta,                               # 5. NÚMERO DE CARTA
        nombre,                              # 6. NOMBRE
        apellido,                            # 7. APELLIDO
        dni,                                 # 8. NÚMERO DE IDENTIDAD
        "",                                  # 9. Columna 8 (Vacia)
        tipo_doc,                            # 10. TIPO DE DOCUMENTO
        fecha_nac.strftime("%d/%m/%Y"),      # 11. FECHA NACIMIENTO
        edad,                                # 12. EDAD
        nacionalidad,                        # 13. NACIONALIDAD
        foto_dni,                            # 14. FOTO DNI/EXTRAVÍO...
        prob_salud,                          # 15. PROBLEMÁTICA DE SALUD
        autovalidez,                         # 16. AUTOVALIDEZ
        cud,                                 # 17. CUD
        cama_baja,                           # 18. SOLICITUD DE CAMA BAJA
        escaleras,                           # 19. APTO PARA SUBIR ESCALERAS
        diag_medico,                         # 20. DIAGNÓSTICO MÉDICO...
        toma_med,                            # 21. TOMA MEDICACIÓN
        cual_med,                            # 22. SI TOMA MEDICACIÓN, ¿CUÁL?
        esquema,                             # 23. CUENTA CON ESQUEMA
        foto_esquema,                        # 24. FOTO DEL ESQUEMA
        posee_med,                           # 25. ¿POSEE LA MEDICACIÓN PARA...
        tiempo_calle,                        # 26. TIEMPO EN CALLE
        motivo_calle,                        # 27. MOTIVO DE SIT. EN CALLE
        primera_vez,                         # 28. PRIMERA VEZ EN CIS
        sit_laboral,                         # 29. SITUACIÓN LABORAL
        desc_trabajo,                        # 30. DESCRIPCIÓN EMPLEO
        desc_trabajo,                        # 31. DE QUÉ TRABAJA (detalle)
        resumen,                             # 32. DIAGNÓSTICO DEL OPERADOR
        doc_ingreso,                         # 33. ¿TIENE LA DOCUMENTACIÓN...?
        panales,                             # 34. ¿USA PAÑALES?
        higieniza,                           # 35. SI LOS USA, SE HIGIENIZA...
        inst_mov,                            # 36. ¿TIENE INSTRUMENTO...?
        cual_inst,                           # 37. SI USA, ¿CUÁL UTILIZA?
        yeso,                                # 38. ¿TIENE YESO...?
        "",                                  # 39. Puntuación
        gorcis                               # 40. SOLO PARA DIPA COMBATE
    ]
    
    sheet = conectar_sheets()
    if sheet:
        sheet.append_row(fila)
        st.success("¡Guardado correctamente!")



