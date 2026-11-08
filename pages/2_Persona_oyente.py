import streamlit as st
from streamlit_mic_recorder import speech_to_text

from mqtt_utils import TOPIC_MENSAJE, get_cliente, publicar

st.title("Persona oyente")
st.caption("Escribe o dicta tu mensaje y llegará a la pantalla del dispositivo.")

client, estado = get_cliente()

RESPUESTAS = {"SI": "Sí", "NO": "No", "AYUDA": "Ayuda"}

# --- Mensaje por texto ---
texto = st.text_input("Escribe tu mensaje")
if st.button("Enviar", type="primary"):
    if texto.strip():
        publicar(TOPIC_MENSAJE, texto.strip())
        st.success(f"Enviado: {texto.strip()}")
    else:
        st.warning("Escribe un mensaje primero.")

# --- Mensaje por voz ---
st.write("O dícta tu mensaje:")
dictado = speech_to_text(
    language="es",
    start_prompt="🎤 Dictar por voz",
    stop_prompt="⏹ Detener",
    just_once=True,
    use_container_width=True,
    key="stt",
)
if dictado:
    publicar(TOPIC_MENSAJE, dictado)
    st.success(f"Enviado por voz: {dictado}")

st.divider()
st.subheader("Respuesta de la persona sorda")


@st.fragment(run_every=2)
def mostrar_respuestas():
    with estado["lock"]:
        recibidas = list(estado["respuestas"])
    if not recibidas:
        st.info("Aún no hay respuestas.")
        return
    ultima = recibidas[-1]
    st.metric("Última respuesta", RESPUESTAS.get(ultima, ultima))
    if ultima == "AYUDA":
        st.warning("La persona sorda necesita ayuda o no entendió el mensaje.")
    if len(recibidas) > 1:
        st.caption("Anteriores: " + ", ".join(RESPUESTAS.get(r, r) for r in reversed(recibidas[:-1])))


mostrar_respuestas()
