# Agent guide — aws-iot-greengrass-v2-edge-walkthrough

Read this and `.kiro/steering/` before changing docs, artifacts, or firmware.
Cursor rules under `.cursor/rules/` mirror the same constraints.

## What this repo is

An **all-in-one** Starlight walkthrough + lab: Greengrass V2 Nucleus on an Intel
NUC6CAY (core) and ESP32-S3 **client devices** (zones), closed-loop sense →
actuate, then AWS integration: cloud deployment from S3, IoT rules → S3 /
DynamoDB / CloudWatch, alarm → SNS → Lambda → cloud-to-edge command, and
SageMaker → ONNX inference on the core.
Cloud and deployments use **visible AWS CLI** and JSON under `artifacts/`.
No Terraform. No provision/deploy wrapper scripts. No CI-driven `aws` apply.

## Before you edit

| Topic | File |
| --- | --- |
| Product / non-goals | `.kiro/steering/product.md` |
| Stack and layout | `.kiro/steering/tech.md` |
| Authoring order | `.kiro/steering/structure.md` |
| Mutation guard | `.kiro/steering/lab-safety.md` |
| AWS claims | `.kiro/steering/aws-source-lock.md` |
| Docs voice | `.kiro/steering/docs-pattern.md` |
| Glossary terms | `.kiro/steering/glossary.md` → `src/data/glossary.ts` |

## Docs glossary

- Every content page that uses a term imports `Tooltip` from `@/components/Tooltip.astro`.
- Prefer first useful occurrence per page; always pass a `label`.
- With `Tooltip` imported, use HTML `<table>` (see `.kiro/steering/markdown-tables.md`).

## Mutation guard

```bash
export GG_EDGE_ALLOW_AWS=1   # operator only, deliberate lab
```

## Docs site

```bash
npm ci
npm run dev
```

Sidebar: **Before you begin** → **1 · Greenhouse on the LAN** →
**2 · Wire into AWS** (Teardown last). Do not assume readers have AWS CLI, Java, jq, or
ESP-IDF already installed.

## Hygiene

- Keep markdown-lint + commitmsg-conform workflows.
- Commit subjects: conform types, US spelling, body required.
- Never commit certs or live `walkthrough.env`.
