# gg-edge-client (ESP32-S3)

ESP-IDF firmware: Greengrass **client device** — discovery, MQTT to Moquette on
the core, button → `gg-edge/sensor`, chip temperature every
`CONFIG_GG_TELEMETRY_INTERVAL_S` (10 s) → `gg-edge/telemetry/<thing>`, RGB ←
`gg-edge/actuator/<thing>`.

Validated on **ESP32-S3** (`idf.py set-target esp32s3`). Needs
[ESP-IDF v5.1+](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/)
(S3 has been supported since IDF v4.4). Lab evidence: IDF **5.3.2** on
Python **3.12**.

## Setup

1. Install [ESP-IDF for ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/)
   (v5.1+) with Ubuntu **Python 3.12** as `python3` when you run `install.sh`
   (see docs Install tooling).
2. Copy client certs from the walkthrough `certs/client/` directory:

```bash
cp ../../certs/client/device.pem.crt main/certs/
cp ../../certs/client/private.pem.key main/certs/
cp ../../certs/client/AmazonRootCA1.pem main/certs/
```

1. Configure Wi‑Fi, Thing name, and IoT endpoint:

```bash
idf.py set-target esp32s3
idf.py menuconfig   # GG Edge Client + Wi‑Fi
idf.py build flash monitor
```

Defaults (ESP32-S3-DevKitC-1): button **GPIO 0** (BOOT); actuator is the
onboard **RGB** (WS2812) — the actuator message picks the color (`green` button
loop, `blue` cloud command, `red` edge ML; default green), `off` = clear. Data pin default
**GPIO 48** (DevKitC-1 v1.0); set `CONFIG_GG_RGB_GPIO=38` for v1.1.

Do not commit PEM files under `main/certs/`.
