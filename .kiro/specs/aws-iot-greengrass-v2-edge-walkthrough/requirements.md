# Requirements — aws-iot-greengrass-v2-edge-walkthrough

## Goal

Document and demonstrate **Greengrass V2 core (NUC) + client device (ESP32-S3)** with a
closed-loop sense → actuate path. Starlight site. AWS CLI for cloud and deployments.

## Must

1. Clear core vs client device distinction (certs, roles, discovery).
2. Documented BOM: NUC (Ubuntu 24.04), ESP32-S3, sensor + actuator for a real loop.
3. Cloud provision via visible AWS CLI (Things, certs, policies, service role).
4. Nucleus install with manual provisioning on the NUC.
5. Deploy Moquette + client device auth + IP detector + MQTT bridge via CLI.
6. ESP32-S3 firmware as a Greengrass client device.
7. Closed-loop custom component + prove steps; teardown checklist.
8. No provision/mqtt-stack wrapper scripts; JSON under `artifacts/` for `file://` CLI.
9. Agents do not mutate AWS without `GG_EDGE_ALLOW_AWS=1`.
10. CI hygiene: markdown-lint + commitmsg-conform; Pages deploy for Starlight.

## Must not (v1)

- Terraform / CDK / SAM.
- Greengrass V1 on the happy path.
- CI that applies AWS resources.
- Hardcoded live account IDs or private keys in committed files.
- Toy demos that skip physical sense→actuate.
