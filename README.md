# 🖥️ secury_pc — Alerta de encendido para equipos propios

Herramienta personal de recuperación ante robo. Cuando el equipo se enciende y
tiene conexión a internet, envía una alerta a tu Telegram con el usuario, el
nombre de la máquina, la IP pública y la ubicación aproximada (por
geolocalización de IP). Si la ciudad cambia respecto al último encendido, marca
la alerta como cambio de ubicación.

La idea: si te roban el equipo, su próximo arranque te avisa desde dónde se
conectó.

## ⚠️ Uso responsable — léelo antes de instalar

Esta herramienta está pensada para instalarse **únicamente en equipos de tu
propiedad**, como medida antirrobo sobre tu propio hardware.

- ✅ **Permitido:** instalarlo en tu portátil o PC para poder localizarlo si te
  lo roban.
- ❌ **Prohibido:** instalarlo en un equipo que no sea tuyo, o en el de otra
  persona sin su conocimiento y consentimiento. Hacerlo puede ser **ilegal**
  (vigilancia no autorizada) en la mayoría de las jurisdicciones.

El autor publica este código con fines educativos y de uso personal legítimo, y
no se responsabiliza por usos indebidos. Si administras equipos de una
organización, informa a las personas usuarias según la legislación aplicable.

> **Nota sobre la ubicación:** el dato proviene de geolocalización por IP
> (servicio `ip-api.com`). **No es GPS**: da la ciudad y una posición aproximada
> del proveedor de internet, no una dirección exacta.

## ✨ Qué reporta

- Usuario del sistema y nombre del equipo
- IP pública e IP local
- Ciudad, región y país aproximados, con enlace a Google Maps
- Aviso destacado cuando cambia la ciudad respecto al último encendido
- Registro local en `log.txt` (excluido del repositorio)

## 🔧 Instalación

```bash
# 1. Clonar
git clone https://github.com/SuazaBrayan9/secury_pc.git
cd secury_pc

# 2. Entorno e instalación de dependencias
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# 3. Configurar credenciales
copy .env.example .env       # Windows  (cp en Linux/Mac)
# Edita .env y coloca tu TOKEN y CHAT_ID
```

Para obtener el token: habla con [@BotFather](https://t.me/BotFather).
Para tu `chat_id`: escríbele a [@userinfobot](https://t.me/userinfobot).

## ▶️ Uso

```bash
python security.py
```

Envía una alerta con el estado actual del equipo. Para que se ejecute en cada
arranque, prográmalo como tarea de inicio del sistema (Programador de tareas en
Windows, `cron @reboot` o un servicio `systemd` en Linux).

## 🔒 Seguridad y privacidad

**Sin secretos en el código.** El `TOKEN` y el `CHAT_ID` se leen de un archivo
`.env` que está excluido del repositorio. La plantilla versionada es
`.env.example`, que solo contiene valores de ejemplo.

**Datos personales fuera del repositorio.** El registro de arranques (`log.txt`)
y la última ubicación (`ultima_ubicacion.json`) contienen datos reales del
equipo y de sus ubicaciones; ambos están en `.gitignore` y nunca se suben.

**Si expones el token,** revócalo de inmediato con `/revoke` en @BotFather y
genera uno nuevo.

## 🛠️ Tecnologías

Python · requests · python-dotenv · API de Telegram Bot · geolocalización por IP

## 📄 Licencia

Distribuido bajo licencia MIT. Ver el archivo [LICENSE](LICENSE).

## 👤 Autor

Steven Suaza Hernández — [@SuazaBrayan9](https://github.com/SuazaBrayan9)
