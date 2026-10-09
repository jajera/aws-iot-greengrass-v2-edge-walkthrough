/**
 * Tooltip glossary for Starlight MDX pages.
 * Keep this list in lockstep with .kiro/steering/glossary.md.
 * Keys: lowercase kebab-case, alphabetical.
 */
export const glossary: Record<string, string> = {
  "aws-cli":
    "AWS Command Line Interface v2 — every cloud and deployment step in this walkthrough is a visible aws command, not a wrapper script.",
  "client-auth":
    "aws.greengrass.clientdevices.Auth — Greengrass component that decides which client device certificates may connect to the local MQTT broker.",
  "client-device":
    "Greengrass client device — an IoT Thing (here the ESP32-S3) that discovers a core and uses local MQTT. It does not run Nucleus.",
  "closed-loop":
    "Sense → decide → actuate on the LAN — zone sensor events on gg-edge/sensor become actuator commands on gg-edge/actuator via a custom component.",
  component:
    "Greengrass component — a versioned unit of software on the core (AWS public components or custom recipes such as GgEdgeLoop / ZoneAnomaly).",
  "core-device":
    "Greengrass core device — the Linux host running Nucleus (this lab: Intel NUC6CAY). Client devices discover and connect to it.",
  discovery:
    "Greengrass discovery API — HTTPS call with the client certificate that returns associated core connectivity (host, port, CA) for local MQTT.",
  "esp-idf":
    "Espressif IoT Development Framework — toolchain used to build and flash the ESP32-S3 client firmware (v5.1+ recommended).",
  "esp32-s3":
    "Espressif ESP32-S3 — Wi‑Fi microcontroller used here as the Greengrass client device (not a second core).",
  "greengrass-cli":
    "Greengrass CLI — local tool under /greengrass/v2/bin/greengrass-cli for listing components and creating local deployments on the core.",
  "greengrass-v2":
    "AWS IoT Greengrass V2 — edge runtime (Nucleus) plus cloud control plane for deployments, client devices, and local MQTT.",
  greenhouse:
    "Example domain for this lab — NUC as edge gateway; ESP32-S3 clients as zones sending telemetry; AWS archives, alarms on, and learns from it, then commands the zones back.",
  iam: "AWS Identity and Access Management — roles for Nucleus token exchange and the Greengrass service role used with client devices.",
  "iot-core":
    "AWS IoT Core — cloud MQTT and device identity service. Client devices use it for discovery; the MQTT bridge forwards zone topics here, where IoT rules route them to other AWS services.",
  "iot-policy":
    "AWS IoT policy — JSON permissions attached to a certificate (core connect/publish; client greengrass:Discover and related actions).",
  "iot-rule":
    "AWS IoT rule — SQL over an MQTT topic filter plus actions (S3, DynamoDB, CloudWatch, …). This is how IoT Core hands bridged Greengrass data to other AWS services.",
  "ip-detector":
    "aws.greengrass.clientdevices.IPDetector — publishes the core's LAN address so discovery returns a reachable host for Moquette.",
  moquette:
    "aws.greengrass.clientdevices.mqtt.Moquette — local MQTT broker on the core. Not Mosquitto; client devices connect here over mTLS.",
  mqtt: "MQTT — publish/subscribe messaging. This lab uses local MQTT to Moquette on the core, bridged to and from IoT Core.",
  "mqtt-bridge":
    "aws.greengrass.clientdevices.mqtt.Bridge — maps topics between LocalMqtt (Moquette), Pubsub (components), and IotCore.",
  mtls: "Mutual TLS — both sides present certificates. The ESP32-S3 authenticates to Moquette with its IoT Thing certificate.",
  nuc6cay:
    "Intel NUC6CAY — compact x86 PC used as the Greengrass core in this lab (spare unit on hand; any quiet Ubuntu 24.04 x86 host works).",
  nucleus:
    "Greengrass Nucleus — the edge runtime on the core device. Installs components, talks to AWS, and hosts the local client-device stack.",
  pubsub:
    "Greengrass interprocess pub/sub — in-process messaging between components on the core (the closed-loop component uses it for sensor/actuator topics).",
  thing:
    "AWS IoT Thing — logical device identity bound to a certificate (core Thing on the NUC; client Thing on the ESP32-S3).",
  "thing-group":
    "AWS IoT Thing group — deployment target for Greengrass cloud deployments (this lab: the core's group).",
  "token-exchange":
    "IoT role alias + IAM role — lets Nucleus exchange its device certificate for temporary AWS credentials on the core.",
  x509: "X.509 certificates — device identity material created with create-keys-and-certificate and stored under certs/ (gitignored).",
};
