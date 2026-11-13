import mediapipe as mp
import numpy as np
import streamlit as st
from PIL import Image

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# 21 puntos x 3 coordenadas (x, y, z) = 63 características
COLUMNAS = ["etiqueta"] + [f"f{i}" for i in range(63)]


@st.cache_resource
def get_detector():
    return mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5,
    )


def normalizar(puntos: np.ndarray, mano: str) -> np.ndarray:
    """Hace que los datos no dependan de dónde está la mano, su tamaño ni cuál mano es."""
    puntos = puntos - puntos[0]            # la muñeca pasa a ser el origen
    if mano == "Left":
        puntos[:, 0] *= -1                 # espeja la mano izquierda para parecerse a la derecha
    escala = np.linalg.norm(puntos[9, :2])  # distancia muñeca -> base del dedo medio
    if escala == 0:
        escala = 1.0
    return (puntos / escala).flatten()


def detectar(imagen_pil, detector):
    """Devuelve (características o None, imagen con el esqueleto dibujado)."""
    rgb = np.array(imagen_pil.convert("RGB"))
    resultado = detector.process(rgb)
    if not resultado.multi_hand_landmarks:
        return None, Image.fromarray(rgb)

    marcas = resultado.multi_hand_landmarks[0]
    mano = resultado.multi_handedness[0].classification[0].label

    anotada = rgb.copy()
    mp_draw.draw_landmarks(anotada, marcas, mp_hands.HAND_CONNECTIONS)

    puntos = np.array([[p.x, p.y, p.z] for p in marcas.landmark])
    return normalizar(puntos, mano), Image.fromarray(anotada)
