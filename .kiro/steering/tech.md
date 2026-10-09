---
inclusion: always
---

# Tech

## Cloud

- Region: prefer `ap-southeast-2` (document if different).
- Tools: **AWS CLI v2 only** for provisioning and deployments — no Terraform, no provision/mqtt-stack wrapper scripts.
- Artifacts: JSON under `artifacts/` passed as `file://` to CLI.
- Services: IoT Core (+ rules), IoT Greengrass V2, IAM, S3, DynamoDB, CloudWatch
  (metrics, alarms, Logs), SNS, Lambda (`python3.14`), SageMaker training
  (prebuilt scikit-learn image, script mode).

## Edge — core

- Hardware: **Intel NUC6CAY** running **Ubuntu 24.04 LTS** (chosen because one was already on hand; any quiet x86 Ubuntu host works).
- Software: Greengrass Nucleus V2 via official installer with **manual** provisioning.
- Local root: `/greengrass/v2` (or `GG_ROOT`); do not commit machine-specific state.

## Edge — client

- Hardware: **ESP32-S3** (Wi‑Fi) as a Greengrass **client device** (not a second core).
- Python **3.12** (Ubuntu 24.04 default) on workstation and NUC — no deadsnakes.
- ESP-IDF **v5.1+** (verified **5.3.2**, venv `idf*_py3.12_env`);
  `idf.py set-target esp32s3`.
- Firmware under `firmware/`; certs only under `certs/` (gitignored except `.gitkeep`).

## Docs site

- **Astro + Starlight**.
- Live site target: `https://aws-iot-greengrass-v2-edge-walkthrough.johna.kiwi/`

## Repo layout

| Path | Purpose |
| --- | --- |
| `src/content/docs/` | Starlight walkthrough pages |
| `src/data/glossary.ts` | Tooltip glossary (lockstep with `.kiro/steering/glossary.md`) |
| `src/components/Tooltip.astro` | Dashed-underline glossary popovers |
| `artifacts/policies/` | IoT policy JSON for `aws iot create-policy` |
| `artifacts/deployments/` | `create-deployment` CLI input JSON |
| `artifacts/components/` | GgEdgeLoop + ZoneAnomaly recipes and artifacts |
| `artifacts/iot-rules/` | `create-topic-rule` payloads |
| `artifacts/lambda/` | Alarm → cloud command Lambda |
| `artifacts/ml/zone-anomaly/` | SageMaker training script + `create-training-job` JSON |
| `artifacts/s3/` | S3 lifecycle JSON |
| `firmware/` | ESP32-S3 client project |
| `config/` | `walkthrough.env.example` naming knobs |
| `certs/` | Local-only material (gitignored) |
| `.kiro/` | Agent steering, hooks, specs |
| `.cursor/rules/` | Cursor project rules |

## Scripts

No `provision.sh` / `deploy.sh`. Optional prove helper only if hand verification is painful.
