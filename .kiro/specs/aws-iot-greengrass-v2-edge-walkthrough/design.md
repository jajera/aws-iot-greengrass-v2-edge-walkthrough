# Design notes

## Roles

- **Core (NUC):** Greengrass Nucleus V2; Moquette; client device auth; IP detector; MQTT bridge; closed-loop component.
- **Client (ESP32-S3):** IoT Thing associated with the core; discovery; local MQTT; sensor publish + actuator subscribe.

## Topics (v1)

| Topic | Direction | Purpose |
| --- | --- | --- |
| `gg-edge/sensor` | ESP32-S3 → broker | Button/sensor events |
| `gg-edge/actuator` | Component → ESP32-S3 | Actuator commands (`on` / `off`) |

MQTT bridge mirrors both to IoT Core for console visibility.

## Provisioning style

- Inline AWS CLI in Starlight pages.
- Policy/deployment JSON in `artifacts/`.
- Operator exports names from `config/walkthrough.env` in the shell; no wrappers.
