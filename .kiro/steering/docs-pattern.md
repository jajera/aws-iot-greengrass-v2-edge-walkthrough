---
inclusion: always
---

# Docs pattern

## Generator

Astro Starlight under `src/content/docs/`. Sidebar order matches the walkthrough sequence.

## Voice

- Prefer **visuals over words**: diagrams, tables, short cards — cut restating prose.
- Imperative steps; short paragraphs.
- Call out **core** vs **client** whenever certs or MQTT endpoints differ.
- Show raw `aws` / installer commands; point at `artifacts/**` with `file://`.
- Cost and teardown get their own pages — not a footnote.
- Import `Tooltip` and use glossary terms (`src/data/glossary.ts`) on first useful
  occurrence — see `glossary.md`. Do not re-define Moquette, Nucleus, or client vs
  core in long asides when a tooltip covers it.
- Mermaid: prefer compact `flowchart` topology on overview pages; reserve
  `sequenceDiagram` for ordered prove/debug steps.

## CLI presentation

- **Command, then result** — put the expected output in the next ` ```text ` block.
  Do **not** write “Looks like:” (or similar) before every result; the adjacent
  blocks are enough.
- Split when each step has a meaningful, distinct result (e.g. `create-thing`,
  then `create-keys-and-certificate`).
- **OK to group** short related setup that shares one result (install zip +
  unzip + `aws --version`, `export` lines, `mkdir`/`cp`/`chmod`, silent
  `attach-*` chains). One text block for the group.
- **Subheads:** use numbered `##` for phases; under a phase with **more than one**
  command (or command group), add a short `###` label per step (no decimals like
  `2.1`). If the `##` title already names a single step, skip a redundant `###`.
- Silent success → `(no output)` in the text block.
- **Never publish real AWS account IDs**, STS caller ARNs, or live IoT endpoint
  host prefixes in the guide. Placeholders: account `123456789012`; endpoint
  prefix `example123abc` (opaque AWS ID — **not** the account number), e.g.
  `example123abc-ats.iot.<region>.amazonaws.com`; truncated cert IDs. Keep live
  values in gitignored `config/walkthrough.env` / `certs/` only.
- Until the evidence pass lands real captures, use realistic shapes and note
  **unverified** in `aws-source-lock.md` / a short page aside where needed.

## Page order

1. Overview (home path map)
2. Tooling
3. Prerequisites
4. Concepts
5. Why Greengrass?
6. Identities
7. Prepare the core
8. Install Nucleus
9. Local MQTT stack
10. Associate zones
11. Loop component
12. Flash zones
13. Prove the LAN loop
14. Deploy from the cloud
15. Archive telemetry
16. Zone state
17. Raise an alarm
18. Cloud commands
19. Edge inference
20. Teardown
21. Troubleshooting
22. AWS docs

## Claims

Every AWS behavioural claim → `aws-source-lock.md` or a docs.aws.amazon.com link.

## Tables

Keep GFM tables valid. Prefer simple two- or three-column tables for BOM and CLI summaries.
