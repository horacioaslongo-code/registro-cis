import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- Configuración de la Página ---
st.set_page_config(page_title="CIS - Gestión de Ingresos", page_icon="🏢", layout="wide")

# Clave de acceso (Cámbiala por la que quieras)
CLAVE_ACCESO = "CIS2025"

# Nombre del archivo local
ARCHIVO_CSV = 'ingresos_detallados.csv'

# --- ENCABEZADOS ---
HEADERS = [
    "ÁREA", "Prioridad", "SUPERVISOR/A", "NÚMERO DE CARTA", "NOMBRE", "APELLIDO",
    "NÚMERO DE IDENTIDAD", "TIPO DE DOCUMENTO", "FECHA NACIMIENTO", "EDAD", "NACIONALIDAD",
    "FOTO DNI/EXTRAVÍO/TRÁMITE", "PROBLEMÁTICA DE SALUD", "AUTOVALIDEZ", "CUD", 
    "SOLICITUD DE CAMA BAJA", "APTO PARA SUBIR ESCALERAS",
    "DIAGNÓSTICO MÉDICO/PSIQUIÁTRICO", "TOMA MEDICACIÓN", "SI TOMA MEDICACIÓN, ¿CUÁL?", 
    "CUENTA CON ESQUEMA", "FOTO DEL ESQUEMA", "¿POSEE LA MEDICACIÓN PARA AL MENOS 2 DÍAS?",
    "TIEMPO EN CALLE", "MOTIVO DE SIT. EN CALLE", "PRIMERA VEZ EN CIS",
    "SITUACIÓN LABORAL", "DESCRIPCIÓN EMPLEO", "DIAGNÓSTICO DEL OPERADOR"
]

# --- Funciones ---
def calcular_edad(fecha_nac):
    if not fecha_nac: return 0
    today = date.today()
    return today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))

def guardar_local(datos_dict):
    df_nuevo = pd.DataFrame([datos_dict])
    if not os.path.exists(ARCHIVO_CSV):
        df_nuevo.to_csv(ARCHIVO_CSV, index=False, columns=HEADERS)
    else:
        df_nuevo.to_csv(ARCHIVO_CSV, mode='a', header=False, index=False, columns=HEADERS)

def verificar_login():
    """Crea una barra lateral de login simple"""
    if 'logueado' not in st.session_state:
        st.session_state['logueado'] = False

    if not st.session_state['logueado']:
        st.markdown("## 🔒 Acceso Restringido CIS")
        col1, col2 = st.columns([1,2])
        with col1:
            password = st.text_input("Ingrese Contraseña de Equipo", type="password")
            if st.button("Ingresar"):
                if password == CLAVE_ACCESO:
                    st.session_state['logueado'] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")
        st.stop() # Detiene la app aquí si no está logueado

# --- EJECUCIÓN PRINCIPAL ---

# 1. Verificar Seguridad
verificar_login()

# 2. Barra Lateral (Menú Administrativo)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/921/921347.png", width=100) # Icono genérico
    st.title("Panel de Control")
    st.markdown("---")
    
    # Descarga de Datos
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        st.metric("Registros Totales", len(df))
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Base de Datos (CSV)",
            csv,
            f"registros_cis_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
        )
    else:
        st.info("Aún no hay registros.")
    
    st.markdown("---")
    if st.button("🔒 Cerrar Sesión"):
        st.session_state['logueado'] = False
        st.rerun()

# 3. Interfaz Principal (Formulario)
st.title("📋 Ficha de Ingreso y Derivación")
st.caption(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

with st.form("formulario_completo", clear_on_submit=True):
    
    # --- BLOQUE 1: DATOS CLAVE ---
    st.subheader("👤 Identificación")
    c1, c2, c3, c4 = st.columns(4)
    with c1: area = st.selectbox("Área", ["RED DE ATENCIÓN", "DIPA 15", "DIPA COMBATE", "SUBTE", "Otro"])
    with c2: dni = st.text_input("DNI (Sin puntos) *")
    with c3: nombre = st.text_input("Nombre *")
    with c4: apellido = st.text_input("Apellido *")
    
    # Lógica DIPA
    gorcis = "NO APLICA"
    if area == "DIPA COMBATE":
        gorcis = st.radio("Evaluación GORCIS?", ["SI", "NO", "NO APLICA"], horizontal=True)

    # --- BLOQUE 2: DETALLES ---
    with st.expander("📝 Datos Complementarios y Salud (Clic para desplegar)", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            fecha_nac = st.date_input("Fecha Nacimiento", min_value=date(1940, 1, 1))
            prioridad = st.selectbox("Prioridad", ["1. COMUNA 2", "2. COMUNA 14", "3. PERSONA SIN TECHO", "4. ORGAS", "5. GERENCIA", "OTRAS"])
            salud = st.selectbox("Problemática Salud", ["NO", "SI"])
            toma_med = st.checkbox("Toma Medicación?")
            cual_med = st.text_input("¿Cuál?") if toma_med else ""
            
        with col_b:
            genero = st.selectbox("Género", ["Masc", "Fem", "Trans", "NB", "Otro"])
            supervisor = st.text_input("Supervisor")
            carta = st.text_input("N° Carta")
            movilidad = st.selectbox("Movilidad Reducida?", ["NO", "SILLA RUEDAS", "MULETAS", "BASTÓN"])

    # --- BLOQUE 3: SOCIAL ---
    st.subheader("🤝 Situación Social")
    obs = st.text_area("Diagnóstico / Resumen del Caso *", height=100, placeholder="Describa brevemente la situación...")

    # Botón grande
    submitted = st.form_submit_button("💾 GUARDAR FICHA", use_container_width=True)

    if submitted:
        if not dni or not nombre or not apellido:
            st.error("⚠️ Faltan datos obligatorios (DNI, Nombre, Apellido)")
        else:
            # Aquí armamos el diccionario (resumido para el ejemplo, agrega todos tus campos)
            datos = {
                "ÁREA": area, "NOMBRE": nombre, "APELLIDO": apellido,
                "NÚMERO DE IDENTIDAD": dni, "DIAGNÓSTICO DEL OPERADOR": obs,
                "FECHA NACIMIENTO": str(fecha_nac),
                "SUPERVISOR/A": supervisor
                # ... (El resto de tus campos irían aquí)
            }
            guardar_local(datos)
            
            # Feedback Moderno
            st.toast(f"✅ Ficha de {nombre} guardada correctamente!", icon="🎉")
            st.balloons()
