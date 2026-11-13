import numpy as np
import streamlit as st
from PIL import Image, ImageOps

from mqtt_utils import TOPIC_SENAS, publicar

st.title("Persona sorda")
st.caption("Haz tu seña frente a la cámara y envíala al dispositivo.")

UMBRAL = 0.80  # confianza mínima para aceptar la seña


@st.cache_resource
def cargar_modelo():
    from tensorflow.keras.models import load_model

    modelo = load_model("modelo/keras_model.h5", compile=False)
    with open("modelo/labels.txt", encoding="utf-8") as f:
        etiquetas = [linea.strip().split(" ", 1)[-1] for linea in f if linea.strip()]
    return modelo, etiquetas


def clasificar(imagen, modelo, etiquetas):
    img = ImageOps.fit(imagen.convert("RGB"), (224, 224), Image.Resampling.LANCZOS)
    x = (np.asarray(img, dtype=np.float32) / 127.5) - 1
    pred = modelo.predict(x[np.newaxis, ...], verbose=0)[0]
    i = int(np.argmax(pred))
    return etiquetas[i], float(pred[i])


try:
    modelo, etiquetas = cargar_modelo()
except Exception as e:
    st.error("No se pudo cargar el modelo. Revisa que keras_model.h5 y labels.txt estén en la carpeta modelo/.")
    st.exception(e)
    st.stop()

foto = st.camera_input("Haz la seña")

if foto is not None:
    etiqueta, confianza = clasificar(Image.open(foto), modelo, etiquetas)

    if etiqueta.strip().lower() == "nada":
        st.info("No veo ninguna seña. Inténtalo de nuevo.")
    elif confianza < UMBRAL:
        st.warning(f"No estoy seguro ({confianza:.0%}). Repite la seña.")
    else:
        st.metric("Seña detectada", etiqueta)
        st.progress(confianza)
        st.caption(f"Confianza: {confianza:.0%}")
        if st.button("Enviar al dispositivo", type="primary"):
            publicar(TOPIC_SENAS, etiqueta)
            st.success(f"Enviado al dispositivo: {etiqueta}")
