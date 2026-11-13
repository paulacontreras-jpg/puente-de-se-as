import pandas as pd
import streamlit as st
from PIL import Image

from hand_utils import COLUMNAS, detectar, get_detector

st.title("Recolectar datos de señas")
st.caption(
    "Haz la seña frente a la cámara, revisa que se dibuje la mano y guarda la muestra. "
    "Hazlo unas 40 veces por seña, variando distancia, ángulo y mano."
)

detector = get_detector()

if "datos" not in st.session_state:
    st.session_state.datos = []
if "cam_n" not in st.session_state:
    st.session_state.cam_n = 0

# --- Continuar con datos de una sesión anterior ---
with st.expander("Cargar datos de una sesión anterior"):
    previo = st.file_uploader("Sube tu CSV", type="csv")
    if previo is not None and st.button("Cargar y agregar a los datos actuales"):
        df_previo = pd.read_csv(previo)
        if list(df_previo.columns) == COLUMNAS:
            st.session_state.datos += df_previo.values.tolist()
            st.success(f"Se cargaron {len(df_previo)} muestras.")
        else:
            st.error("El archivo no tiene el formato esperado.")

# --- Captura ---
etiqueta = st.text_input("Seña que vas a grabar (por ejemplo: A, B, L)").strip().upper()
foto = st.camera_input("Haz la seña", key=f"cam_{st.session_state.cam_n}")

if foto is not None:
    caracteristicas, anotada = detectar(Image.open(foto), detector)
        st.image(anotada, caption="Lo que ve el detector", output_format="PNG", use_container_width=True)

    if caracteristicas is None:
        st.warning("No se detectó la mano. Acércate, usa más luz y vuelve a tomar la foto.")
    elif not etiqueta:
        st.info("Escribe arriba qué seña estás grabando para poder guardarla.")
    else:
        if st.button(f"Guardar muestra de «{etiqueta}»", type="primary"):
            st.session_state.datos.append([etiqueta] + caracteristicas.tolist())
            st.session_state.cam_n += 1   # reinicia la cámara para la siguiente foto
            st.rerun()

# --- Resumen y descarga ---
st.divider()
df = pd.DataFrame(st.session_state.datos, columns=COLUMNAS)
st.subheader(f"Muestras guardadas: {len(df)}")

if len(df) > 0:
    st.bar_chart(df["etiqueta"].value_counts())

    col1, col2 = st.columns(2)
    col1.download_button(
        "Descargar CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="landmarks.csv",
        mime="text/csv",
        type="primary",
    )
    if col2.button("Borrar la última muestra"):
        st.session_state.datos.pop()
        st.rerun()

st.warning(
    "Los datos viven en la memoria de la app: si recargas la página o la app se reinicia, "
    "se pierden. Descarga el CSV con frecuencia."
)
