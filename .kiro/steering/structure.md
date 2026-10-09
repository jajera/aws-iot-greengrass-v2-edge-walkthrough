---
inclusion: always
---

# Structure

## Authoring order

1. Steering + AGENTS.md + Cursor rules.
2. Starlight scaffold + page stubs.
3. `artifacts/` JSON + identities/nucleus/mqtt-stack docs (CLI inline).
4. Loop component + ESP32-S3 firmware + prove-lan.
5. Act 2 pages (deploy-cloud → archive → zone-state → alarm → command → inference) + teardown.
6. Evidence pass: run once, lock facts in `aws-source-lock.md`.

## Naming

- Repo: `aws-iot-greengrass-v2-edge-walkthrough`
- Mutation opt-in: `GG_EDGE_ALLOW_AWS=1`
- Prefer US spelling in commit subjects (conform + spellcheck).

## What not to commit

- Private keys, device certs, live `walkthrough.env`
- Nucleus `config.yaml` from a live install
- Large binary firmware artifacts unless explicitly required
