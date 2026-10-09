---
inclusion: always
---

# Product

Walkthrough: **AWS IoT Greengrass V2 greenhouse edge lab** — Intel NUC6CAY as
**core**, up to three ESP32-S3 boards as **client devices** (zones), closed-loop
sense → local MQTT on the core → actuate, then **integration with other AWS
services**: the bridge carries zone telemetry to IoT Core, where rules feed S3,
DynamoDB, and CloudWatch; alarms drive commands back to the zones via SNS →
Lambda; SageMaker trains on the S3 telemetry and the ONNX model runs on the core.
Maps AWS-marketed Concepts (deployments, S3 artifacts, components,
data exchange, edge ML) onto real hardware — not an EC2-as-edge Skill Builder toy.

The NUC6CAY is the documented host because one was already on the shelf — any quiet
x86 box is fine. Core host OS is **Ubuntu Server 24.04 LTS** (via shared
**ubuntu-server-walkthrough**; lab names on **Prepare the core**). **AWS CLI** for
all cloud and deployment steps. Starlight docs site.

## Audience

Engineers who have used IoT Core or MQTT before, but have not stood up Greengrass V2
Nucleus + client devices end to end — and want the poster story (fleet deploy, S3
artifacts, cloud data integration, edge ML) without losing a real LAN closed loop.

## Outcomes

1. Understand core vs client (certs, roles, discovery) and when Greengrass beats
   direct IoT Core (and when it does not — SPOF).
2. Install Nucleus on Ubuntu on the NUC6CAY with **manual** provisioning (visible CLI).
3. Deploy AWS client-device components (Moquette, auth, IP detector, MQTT bridge).
4. Provision ESP32-S3 clients (one required; up to three zones); closed-loop sense →
   actuate on the LAN (button → green RGB), plus chip-temperature telemetry.
5. Act 2 (Wire into AWS) as one continuous demo after prove-lan: local CLI → S3 artifact →
   cloud deployment (with LogManager → CloudWatch Logs); IoT rules → S3 telemetry
   lake, DynamoDB zone state, CloudWatch metric + alarm → SNS; Lambda → cloud →
   edge command (blue RGB); SageMaker training on the lake → ONNX → Greengrass
   component inference on the NUC (red RGB). Not Edge Manager (EOL).
6. Cost-aware teardown of every resource, last in the sidebar.

## Non-goals (v1)

- Greengrass V1
- Terraform / CDK / SAM
- Provision or deploy wrapper scripts that hide CLI
- EC2 / VPC as the documented edge host (contrast only)
- SageMaker Edge Manager (EOL 2024-04-26)
- Stream Manager, ESP32 firmware OTA, IoT Analytics, Device Defender
- Production multi-core HA or multi-region
- Toy GPIO demos that skip real sense→actuate
- High-level "optional lab" pages without runnable CLI and observable proof
- Docker component lab
- Mosquitto-only lab that never uses Greengrass
