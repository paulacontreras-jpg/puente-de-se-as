import random
import threading
import unicodedata

import paho.mqtt.client as mqtt
import streamlit as st

BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC_SENAS = "pau/puente/senas"
TOPIC_MENSAJE = "pau/puente/mensaje"
TOPIC_RESPUESTA = "pau/puente/respuesta"


def limpiar_texto(texto: str) -> str:
    """Quita tildes y signos que la LCD no puede mostrar."""
    texto = texto.replace("¿", "").replace("¡", "")
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


@st.cache_resource
def get_cliente():
    """Crea un único cliente MQTT en segundo plano para toda la app."""
    estado = {"respuestas": [], "conectado": False, "lock": threading.Lock()}

    def on_connect(client, userdata, flags, rc):
        estado["conectado"] = (rc == 0)
        client.subscribe(TOPIC_RESPUESTA)

    def on_disconnect(client, userdata, rc):
        estado["conectado"] = False

    def on_message(client, userdata, msg):
        texto = msg.payload.decode("utf-8", errors="ignore")
        with estado["lock"]:
            estado["respuestas"].append(texto)
            del estado["respuestas"][:-20]  # conserva las últimas 20

    client = mqtt.Client(client_id=f"streamlit-puente-{random.randint(0, 99999)}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    return client, estado


def publicar(topic: str, texto: str) -> None:
    client, _ = get_cliente()
    client.publish(topic, limpiar_texto(texto))
