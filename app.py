import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- Configuración de la Página ---
st.set_page_config(page_title="Formulario de Ingreso Social", page_icon="📋", layout="wide")

# Nombre del archivo local (Respaldo)
ARCHIVO_CSV = 'ingresos_detallados.csv'

# --- ENCABEZADOS EXACTOS SOLICITADOS ---
HEADERS = [
    "ÁREA", "Prioridad", "SUPERVISOR/A", "NÚMERO DE CARTA", "NOMBRE", "APELLIDO",
    "NÚMERO DE IDENTIDAD", "TIPO DE DOCUMENTO", "FECHA NACIMIENTO", "EDAD", "NACIONALIDAD",
    "FOTO DNI/EXTRAVÍO/TRÁMITE (ya enviadas al grupo de wpp)",
    "PROBLEMÁTICA DE SALUD", "AUTOVALIDEZ", "CUD", "SOLICITUD DE CAMA BAJA",
    "APTO PARA SUBIR ESCALERAS",
    "DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO (acá también especificar el por qué necesita cama abajo)",
    "TOMA MEDICACIÓN", "SI TOMA MEDICACIÓN, ¿CUÁL?", "CUENTA CON ESQUEMA",
    "FOTO DEL ESQUEMA (ya enviada al grupo de Wpp)",
    "¿POSEE LA MEDICACIÓN PARA AL MENOS 2 DÍAS?",
    "TIEMPO EN CALLE", "MOTIVO DE SIT. EN CALLE", "PRIMERA VEZ EN CIS",
    "SITUACIÓN LABORAL", "DESCRIPCIÓN EMPLEO", # Agregado para capturar el rubro/modalidad
    "DIAGNÓSTICO DEL OPERADOR Y RESUMEN DEL CASO"
]

# --- Funciones Auxiliares ---
def calcular_edad(fecha_nac):
    if not fecha_nac: return 0
    today = date.today()
    return today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))

def guardar_local(datos_dict):
    df_nuevo = pd.DataFrame([datos_dict])
    
    # Si el archivo no existe, crearlo con headers
    if not os.path.exists(ARCHIVO_CSV):
        df_nuevo.to_csv(ARCHIVO_CSV, index=False, columns=HEADERS)
    else:
        # Si existe, agregar sin headers
        df_nuevo.to_csv(ARCHIVO_CSV, mode='a', header=False, index=False, columns=HEADERS)

# --- Interfaz de Usuario ---
st.title("📋 Ficha de Ingreso y Derivación")
st.markdown("Complete los campos requeridos. Los campos con (*) son obligatorios.")

with st.form("formulario_completo", clear_on_submit=True):
    
    # --- SECCIÓN 1: DATOS ADMINISTRATIVOS ---
    st.markdown("### 1. Datos Administrativos y Prioridad")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        area = st.selectbox("ÁREA *", [
            "RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE", "Otro"
        ])
        
        # Lógica condicional para DIPA COMBATE
        evaluacion_gorcis = "NO APLICA"
        if area == "DIPA COMBATE":
            st.info("🔹 Pregunta específica para DIPA COMBATE")
            evaluacion_gorcis = st.radio("¿Se requiere evaluación equipo discapacidad GORCIS?", ["SI", "NO", "NO APLICA"])
        
        otro_area = ""
        if area == "Otro":
            otro_area = st.text_input("Especifique Área")

    with col2:
        prioridad = st.selectbox("Prioridad *", [
            "1. COMUNA 2", "2. COMUNA 14", "3. PERSONA SIN TECHO", 
            "4. ORGAS", "5. GERENCIA", "6. 9 DE JULIO", "7. OTRAS"
        ])
        
    with col3:
        supervisor = st.text_input("SUPERVISOR/A *")
        carta = st.text_input("NÚMERO DE CARTA *")

    st.divider()

    # --- SECCIÓN 2: DATOS PERSONALES ---
    st.markdown("### 2. Datos Personales")
    c_p1, c_p2, c_p3 = st.columns(3)
    
    with c_p1:
        apellido = st.text_input("APELLIDO *")
        nombre = st.text_input("NOMBRE *")
        nacionalidad = st.text_input("NACIONALIDAD")
        
    with c_p2:
        tipo_doc = st.selectbox("TIPO DE DOCUMENTO *", ["DNI", "Pasaporte", "Precaria", "Indocumentado", "Otro"])
        dni = st.text_input("NÚMERO DE IDENTIDAD *", placeholder="Sin puntos. Ej: 30451327")
        
    with c_p3:
        fecha_nac = st.date_input("FECHA NACIMIENTO", min_value=date(1920, 1, 1))
        # Cálculo automático de edad para mostrar en pantalla
        edad_calc = calcular_edad(fecha_nac)
        st.write(f"🧮 **Edad calculada:** {edad_calc} años")
    
    # Documentación
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        doc_necesaria = st.radio("¿TIENE LA DOCUMENTACIÓN NECESARIA PARA EL INGRESO A CIS? *", ["SI", "NO"], horizontal=True)
    with c_d2:
        foto_dni = st.radio("FOTO DNI/EXTRAVÍO/TRÁMITE (ya enviadas al grupo de wpp) *", ["SI", "NO"], horizontal=True)

    st.divider()

    # --- SECCIÓN 3: SALUD Y MOVILIDAD ---
    st.markdown("### 3. Salud, Medicación y Movilidad")
    
    # Salud General
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        prob_salud = st.selectbox("PROBLEMÁTICA DE SALUD *", ["NO", "SI"])
        cud = st.selectbox("CUD *", ["NO", "SI", "NO REQUIERE"])
    with c_s2:
        autovalidez = st.selectbox("AUTOVALIDEZ *", ["SI", "NO"])
        cama_baja = st.selectbox("SOLICITUD DE CAMA BAJA *", ["NO", "SI"])
    with c_s3:
        escaleras = st.selectbox("APTO PARA SUBIR ESCALERAS *", ["SI", "NO"])
    
    diag_medico = st.text_area("DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO (Especificar por qué necesita cama baja)")
    
    # Medicación (Lógica condicional)
    st.markdown("#### 💊 Medicación")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        toma_med = st.selectbox("TOMA MEDICACIÓN *", ["NO", "SI"])
        cual_med = ""
        esquema = "NO REQUIERE"
        foto_esquema = "NO REQUIERE"
        posee_meds = "NO REQUIERE"
        
        if toma_med == "SI":
            cual_med = st.text_input("SI TOMA MEDICACIÓN, ¿CUÁL?")
            esquema = st.radio("CUENTA CON ESQUEMA", ["SI", "NO"], horizontal=True)
            foto_esquema = st.radio("FOTO DEL ESQUEMA (Enviada a Wpp)", ["SI", "NO"], horizontal=True)
            posee_meds = st.radio("¿POSEE LA MEDICACIÓN PARA AL MENOS 2 DÍAS?", ["SI", "NO"], horizontal=True)

    # Higiene y Movilidad
    st.markdown("#### ♿ Movilidad e Higiene")
    c_h1, c_h2 = st.columns(2)
    with c_h1:
        usa_panales = st.selectbox("¿USA PAÑALES? *", ["NO", "SI"])
        if usa_panales == "SI":
            st.radio("SI LOS USA , ¿PUEDE HIGIENIZARSE SOLO?", ["Sí", "NO"])
            
    with c_h2:
        inst_movilidad = st.selectbox("¿TIENE INSTRUMENTO PARA MOVILIDAD? *", ["NO", "SI"])
        tipo_movilidad = "NINGUNO"
        if inst_movilidad == "SI":
            tipo_movilidad = st.selectbox("SI USA, ¿CUÁL UTILIZA?", ["SILLA DE RUEDAS", "BASTON", "ANDADOR", "MULETAS"])
            
        yeso = st.selectbox("¿TIENE YESO O PARTE INMOVILIZADA? *", ["NO", "SI"])

    st.divider()

    # --- SECCIÓN 4: SITUACIÓN SOCIAL Y LABORAL ---
    st.markdown("### 4. Situación Social y Laboral")
    
    c_soc1, c_soc2 = st.columns(2)
    with c_soc1:
        tiempo_calle = st.selectbox("TIEMPO EN CALLE *", [
            "NO RECUERDA", "MENOS DE 1 MES", "MAS DE 1 MES", 
            "ENTRE 1 Y 6 MESES", "ENTRE 6 MESES Y 1 AÑO", 
            "MAS DE 1 AÑO", "MAS DE 2 AÑOS"
        ])
        motivo_calle = st.selectbox("MOTIVO DE SIT. EN CALLE *", [
            "MOTIVO ECONÓMICO", "MOTIVO FAMILIAR", "MOTIVO SALUD", "OTROS MOTIVOS"
        ])
        primera_vez = st.radio("PRIMERA VEZ EN CIS *", ["SI", "NO"], horizontal=True)

    with c_soc2:
        sit_laboral = st.selectbox("SITUACIÓN LABORAL *", [
            "Posee empleo", 
            "Desempleado. En búsqueda activa", 
            "Desempleado. Sin búsqueda activa", 
            "Desempleado debido a imposibilidad de trabajar (discapacidad/salud mental)"
        ])
        
        desc_empleo = ""
        if sit_laboral == "Posee empleo":
            desc_empleo = st.text_input("DE QUÉ TRABAJA (modalidad, dónde, rubro, horas, etc) *")

    st.markdown("---")
    resumen_caso = st.text_area("DIAGNÓSTICO DEL OPERADOR Y RESUMEN DEL CASO *", height=100)

    # --- BOTÓN DE ENVÍO ---
    submitted = st.form_submit_button("✅ GUARDAR Y REGISTRAR", use_container_width=True)

    if submitted:
        # Validaciones básicas
        if not apellido or not nombre or not dni:
            st.error("⚠️ Falta completar Nombre, Apellido o DNI.")
        else:
            # Construir el diccionario EXACTO para Google Sheets
            datos_registro = {
                "ÁREA": f"{area} ({evaluacion_gorcis})" if area == "DIPA COMBATE" else area,
                "Prioridad": prioridad,
                "SUPERVISOR/A": supervisor,
                "NÚMERO DE CARTA": carta,
                "NOMBRE": nombre,
                "APELLIDO": apellido,
                "NÚMERO DE IDENTIDAD": dni,
                "TIPO DE DOCUMENTO": tipo_doc,
                "FECHA NACIMIENTO": fecha_nac.strftime("%d/%m/%Y"),
                "EDAD": edad_calc,
                "NACIONALIDAD": nacionalidad,
                "FOTO DNI/EXTRAVÍO/TRÁMITE (ya enviadas al grupo de wpp)": foto_dni,
                "PROBLEMÁTICA DE SALUD": prob_salud,
                "AUTOVALIDEZ": autovalidez,
                "CUD": cud,
                "SOLICITUD DE CAMA BAJA": cama_baja,
                "APTO PARA SUBIR ESCALERAS": escaleras,
                "DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO (acá también especificar el por qué necesita cama abajo)": diag_medico,
                "TOMA MEDICACIÓN": toma_med,
                "SI TOMA MEDICACIÓN, ¿CUÁL?": cual_med,
                "CUENTA CON ESQUEMA": esquema,
                "FOTO DEL ESQUEMA (ya enviada al grupo de Wpp)": foto_esquema,
                "¿POSEE LA MEDICACIÓN PARA AL MENOS 2 DÍAS?": posee_meds,
                "TIEMPO EN CALLE": tiempo_calle,
                "MOTIVO DE SIT. EN CALLE": motivo_calle,
                "PRIMERA VEZ EN CIS": primera_vez,
                "SITUACIÓN LABORAL": sit_laboral,
                "DESCRIPCIÓN EMPLEO": desc_empleo, # Este campo mapea a "DE QUE TRABAJA"
                "DIAGNÓSTICO DEL OPERADOR Y RESUMEN DEL CASO": resumen_caso
            }
            
            # Guardar en CSV local (Backup)
            guardar_local(datos_registro)
            
            st.success("✅ Registro guardado exitosamente.")
            st.balloons()
            
            # Mostrar lo que se guardó
            with st.expander("Ver datos registrados"):
                st.json(datos_registro)

# --- PANEL DE DESCARGA PARA EXCEL/SHEETS ---
st.markdown("---")
st.subheader("📂 Gestión de Datos")

if os.path.exists(ARCHIVO_CSV):
    df = pd.read_csv(ARCHIVO_CSV)
    st.write(f"Total de registros: {len(df)}")
    
    # Botón para descargar CSV compatible con Google Sheets
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Descargar Planilla para Google Sheets",
        csv,
        "planilla_cis.csv",
        "text/csv",
        key='download-csv'
    )
