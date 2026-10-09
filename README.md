# aws-iot-greengrass-v2-edge-walkthrough

End-to-end **AWS IoT Greengrass V2** lab: Nucleus on an Intel **NUC6CAY**
(**core**), up to three ESP32-S3 boards (**client** zones), closed-loop sense →
actuate on the LAN, then integration with AWS: cloud deployment from S3,
IoT rules → S3 telemetry lake / DynamoDB zone state / CloudWatch alarm → SNS →
Lambda → cloud-to-edge command, and a SageMaker-trained ONNX model running on
the core.
Cloud steps use **visible AWS CLI** and JSON under `artifacts/` — no
provision/deploy wrappers.

**Docs site:** [aws-iot-greengrass-v2-edge-walkthrough.johna.kiwi](https://aws-iot-greengrass-v2-edge-walkthrough.johna.kiwi/) (after Pages deploy).

## Quick start (docs)

```bash
npm ci
npm run dev
```

## Lab config

```bash
cp config/walkthrough.env.example config/walkthrough.env
set -a && source config/walkthrough.env && set +a
```

Follow the Starlight sidebar: **Before you begin** → **1 · Greenhouse on the LAN** →
**2 · Wire into AWS** (Teardown last).

Host OS install: [Ubuntu Server walkthrough](https://ubuntu-server-walkthrough.johna.kiwi/)
(linked from Prepare the core; this repo only adds lab hostname / `walkthrough.env`).

Mutation guard for agents: `GG_EDGE_ALLOW_AWS=1`.

## Layout

| Path | Role |
| --- | --- |
| `src/content/docs/` | Starlight walkthrough |
| `artifacts/policies/` | IoT / IAM policy JSON for `file://` CLI |
| `artifacts/deployments/` | `create-deployment` input JSON |
| `artifacts/components/` | GgEdgeLoop (1.0.1 local, 1.1.0 cloud), ZoneAnomaly (ONNX) |
| `artifacts/iot-rules/` | `create-topic-rule` payloads (S3, DynamoDB, CloudWatch) |
| `artifacts/lambda/` | Alarm → cloud command Lambda |
| `artifacts/ml/zone-anomaly/` | SageMaker training script + job JSON |
| `artifacts/s3/` | Data bucket lifecycle |
| `firmware/gg-edge-client/` | ESP-IDF client firmware |
| `config/` | Naming env example |
| `certs/` | Local cert output (gitignored) |
| `AGENTS.md` | Agent entrypoint |
| `.kiro/` | Steering, hooks, specs |

## Architecture

- **Core** — Ubuntu 24.04 on NUC6CAY, Nucleus, Moquette, client auth, IP detector, MQTT bridge, LogManager, GgEdgeLoop, ZoneAnomaly
- **Client** — ESP32-S3 zones discover the core, MQTT to Moquette; button → `gg-edge/sensor`, chip temperature → `gg-edge/telemetry/<thing>`, RGB ← `gg-edge/actuator/<thing>`
- **Cloud** — IoT identity and discovery; S3 artifacts + Greengrass deployments; IoT rules → S3, DynamoDB, CloudWatch; alarm → SNS → Lambda → `gg-edge/cloud/command/<thing>`; SageMaker training → ONNX; CloudWatch Logs

## Agent / Kiro / Cursor

Read [AGENTS.md](AGENTS.md) and `.kiro/steering/` before changing docs or firmware.
