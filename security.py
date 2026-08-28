# -*- coding: utf-8 -*-
"""
secury_pc — Alerta de encendido para equipos propios.

Al ejecutarse, recopila datos básicos del equipo (usuario, nombre de máquina,
IP pública y ubicación aproximada por geolocalización de IP) y los envía a un
chat de Telegram definido por el dueño. Pensado para instalarse como tarea de
arranque en un equipo PROPIO, de modo que si es robado, su próximo encendido
con conexión a internet envíe una alerta.

Uso ético: instálalo únicamente en equipos de tu propiedad. Ver README.
"""
import os
import json
import socket
import getpass
import logging
import platform
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LOG_FILE = "log.txt"
UBICACION_FILE = "ultima_ubicacion.json"
HTTP_TIMEOUT = 10  # segundos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def obtener_ip_publica() -> str:
    try:
        r = requests.get("https://api.ipify.org", timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.text.strip()
    except requests.RequestException as e:
        logger.warning("No se pudo obtener la IP pública: %s", e)
        return "No disponible"


def obtener_ip_local() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError as e:
        logger.warning("No se pudo obtener la IP local: %s", e)
        return "No disponible"


def obtener_ubicacion(ip_publica: str):
    """Geolocalización aproximada por IP. Nunca es GPS: es a nivel de ciudad."""
    vacio = ("Desconocido", "", "", "", "", "")
    if ip_publica in ("No disponible", ""):
        return vacio
    try:
        r = requests.get(f"http://ip-api.com/json/{ip_publica}", timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success":
            lat, lon = data.get("lat", ""), data.get("lon", "")
            mapa = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            return (
                data.get("city", "Desconocido"),
                data.get("regionName", ""),
                data.get("country", ""),
                lat, lon, mapa,
            )
    except (requests.RequestException, ValueError) as e:
        logger.warning("No se pudo obtener la ubicación: %s", e)
    return vacio


def registrar_log(mensaje: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} - {mensaje}\n")
    except OSError as e:
        logger.warning("No se pudo escribir en el log: %s", e)


def verificar_cambio_ubicacion(ciudad_actual: str):
    """Devuelve (hubo_cambio, ciudad_anterior) y persiste la ciudad nueva."""
    ciudad_anterior = None
    try:
        if os.path.exists(UBICACION_FILE):
            with open(UBICACION_FILE, "r", encoding="utf-8") as f:
                ciudad_anterior = json.load(f).get("ciudad")
        with open(UBICACION_FILE, "w", encoding="utf-8") as f:
            json.dump({"ciudad": ciudad_actual}, f)
    except (OSError, ValueError) as e:
        logger.warning("No se pudo leer/guardar la última ubicación: %s", e)
        return False, None
    if ciudad_anterior is not None and ciudad_actual != ciudad_anterior:
        return True, ciudad_anterior
    return False, None


def enviar_alerta() -> None:
    if not TOKEN or not CHAT_ID:
        logger.error(
            "Faltan TOKEN o CHAT_ID. Copia .env.example a .env y complétalos."
        )
        return

    hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = getpass.getuser()
    equipo = platform.node()
    ip_local = obtener_ip_local()
    ip_publica = obtener_ip_publica()
    ciudad, region, pais, lat, lon, enlace_mapa = obtener_ubicacion(ip_publica)
    cambio_ubicacion, ciudad_anterior = verificar_cambio_ubicacion(ciudad)

    mensaje = (
        f"🖥️ *Alerta de encendido*\n\n"
        f"👤 Usuario: `{usuario}`\n"
        f"💻 Equipo: `{equipo}`\n"
        f"🕒 Hora: `{hora}`\n"
        f"🌐 IP pública: `{ip_publica}`\n"
        f"📡 IP local: `{ip_local}`\n"
        f"📍 Ubicación: `{ciudad}, {region}, {pais}`\n"
        f"🌎 Coordenadas: `{lat}, {lon}`\n"
        f"🗺️ [Ver en Google Maps]({enlace_mapa})"
    )
    if cambio_ubicacion:
        mensaje += (
            f"\n\n⚠️ *¡Alerta!* Se detectó un cambio de ciudad.\n"
            f"📍 Anterior: `{ciudad_anterior}`"
        )

    registrar_log(f"{usuario} - {equipo} - {ciudad} - {ip_publica} - {hora}")

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        logger.info("Alerta enviada correctamente.")
    except requests.RequestException as e:
        logger.error("Error al enviar el mensaje a Telegram: %s", e)


if __name__ == "__main__":
    enviar_alerta()
