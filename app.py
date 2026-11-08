import streamlit as st

st.set_page_config(page_title="Puente de Señas", page_icon="🤟")

st.title("🤟 Puente de Señas")
st.write(
    "Sistema de comunicación multimodal entre una persona sorda y una persona "
    "oyente, conectado a un dispositivo simulado en Wokwi mediante MQTT."
)

st.page_link("pages/1_Persona_sorda.py", label="Persona sorda (cámara)", icon="📷")
st.page_link("pages/2_Persona_oyente.py", label="Persona oyente (texto y voz)", icon="💬")
