import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
import os
from datetime import date, timedelta

# --- CONFIGURACIÓN INSTITUCIONAL ---
st.set_page_config(page_title="ISFD n° 16 - Calendario Académico", page_icon="🎓", layout="wide")

CLAVE_DIRECTOR = "calendariomgd26" 
ARCHIVO_DATOS = "datos_isfd16.csv"

# --- ENCABEZADO ---
st.markdown(f"<h1 style='text-align: center; color: #1C83E1;'>ISFD n° 16</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 24px; font-weight: bold;'>Calendario Académico</p>", unsafe_allow_html=True)
st.write("---")

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            return pd.read_csv(ARCHIVO_DATOS)
        except:
            return pd.DataFrame(columns=["Inicio", "Fin", "Evento", "Categoría"])
    return pd.DataFrame(columns=["Inicio", "Fin", "Evento", "Categoría"])

df = cargar_datos()

# --- CONFIGURACIÓN DE COLORES SOLICITADA ---
colores = {
    "Examen": "#87CEEB",                # Celeste (Pedido)
    "Suspensión de Actividades": "#F1C40F", # Amarillo (Pedido)
    "Feriado": "#E74C3C",               # Rojo (Pedido)
    "Jornada Institucional": "#8E44AD", # Violeta
    "Jornada Curricular": "#D35400",    # Naranja
    "Cambio de Actividad": "#1ABC9C",   # Turquesa
    "Paro de Aten": "#E67E22",          # Naranja oscuro
    "Otro": "#95A5A6",                  # Gris
    "1° Cuatrimestre": "#2E86C1",       # Azul fuerte
    "2° Cuatrimestre": "#28B463",       # Verde
    "Receso Invernal": "#34495E"        # Azul grisáceo
}

tab_estudiantes, tab_direccion = st.tabs(["👥 VISTA ESTUDIANTES", "🔐 PANEL DE DIRECCIÓN"])

with tab_estudiantes:
    st.info("Bienvenido. Consulta aquí las fechas oficiales del ISFD n° 16.")
    calendar_events = []

    for i, row in df.iterrows():
        calendar_events.append({
            "title": f"{row['Evento']} ({row['Categoría']})",
            "start": row['Inicio'],
            "end": (pd.to_datetime(row['Fin']) + timedelta(days=1)).strftime('%Y-%m-%d'),
            "color": colores.get(row['Categoría'], "#3D3333"),
            "allDay": True
        })

    calendar_options = {
        "locale": "es",
        "headerToolbar": {"left": "prev,next hoy", "center": "title", "right": "dayGridMonth"},
        "buttonText": {"today": "Hoy", "month": "Mes"},
        "initialView": "dayGridMonth",
    }

    calendar(events=calendar_events, options=calendar_options)
    
    if not df.empty:
        with st.expander("Ver lista de eventos detallada"):
            df_v = df.copy()
            df_v['Inicio'] = pd.to_datetime(df_v['Inicio']).dt.strftime('%d/%m/%Y')
            df_v['Fin'] = pd.to_datetime(df_v['Fin']).dt.strftime('%d/%m/%Y')
            st.dataframe(df_v, use_container_width=True, hide_index=True)

with tab_direccion:
    password = st.text_input("Ingrese Clave de Director:", type="password")
    if password == CLAVE_DIRECTOR:
        st.success("Acceso Autorizado")
        subtab_add, subtab_edit, subtab_del = st.tabs(["➕ Añadir", "📝 Modificar", "🗑️ Eliminar"])

        with subtab_add:
            with st.form("form_add", clear_on_submit=True):
                n_new = st.text_input("Nombre del evento")
                c1, c2 = st.columns(2)
                with c1: f_i = st.date_input("Inicio:", date.today())
                with c2: f_f = st.date_input("Fin:", date.today())
                t_new = st.selectbox("Categoría:", list(colores.keys()))
                if st.form_submit_button("Publicar Evento"):
                    if n_new:
                        nueva_fila = pd.DataFrame([[str(f_i), str(f_f), n_new, t_new]], 
                                                 columns=["Inicio", "Fin", "Evento", "Categoría"])
                        df = pd.concat([df, nueva_fila], ignore_index=True)
                        df.to_csv(ARCHIVO_DATOS, index=False)
                        st.rerun()

        with subtab_edit:
            if not df.empty:
                opciones = [f"{i}: {row['Evento']} ({row['Inicio']})" for i, row in df.iterrows()]
                seleccion = st.selectbox("Seleccione para modificar:", opciones)
                index_to_edit = int(seleccion.split(":")[0])
                row_data = df.iloc[index_to_edit]
                with st.form("form_edit"):
                    n_edit = st.text_input("Nombre:", value=row_data['Evento'])
                    c1, c2 = st.columns(2)
                    with c1: f_i_edit = st.date_input("Inicio:", pd.to_datetime(row_data['Inicio']))
                    with c2: f_f_edit = st.date_input("Fin:", pd.to_datetime(row_data['Fin']))
                    t_edit = st.selectbox("Categoría:", list(colores.keys()), index=list(colores.keys()).index(row_data['Categoría']))
                    if st.form_submit_button("Guardar Cambios"):
                        df.at[index_to_edit, 'Evento'] = n_edit
                        df.at[index_to_edit, 'Inicio'] = str(f_i_edit)
                        df.at[index_to_edit, 'Fin'] = str(f_f_edit)
                        df.at[index_to_edit, 'Categoría'] = t_edit
                        df.to_csv(ARCHIVO_DATOS, index=False)
                        st.rerun()

        with subtab_del:
            if not df.empty:
                opciones_del = [f"{i}: {row['Evento']} ({row['Inicio']})" for i, row in df.iterrows()]
                seleccion_del = st.selectbox("Seleccione para eliminar:", opciones_del)
                index_to_del = int(seleccion_del.split(":")[0])
                if st.button("Confirmar Eliminación"):
                    df = df.drop(index_to_del).reset_index(drop=True)
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.rerun()
    elif password != "":
        st.error("Contraseña incorrecta")
