---
inclusion: fileMatch
fileMatchPattern: "src/data/glossary*"
---

# Glossary conventions

## File structure

- Glossary lives in `src/data/glossary.ts`
- Type: `Record<string, string>` — key is the term slug, value is the definition
- Keep entries in **alphabetical order** by key
- Keys use lowercase kebab-case (e.g. `iot-core`, `mqtt-bridge`)

## Definition style

- Start with the expanded form / full name or component name
- One or two sentences max
- Include walkthrough-specific context (topics, host, component names) when helpful

## Usage in pages

```mdx
import Tooltip from "@/components/Tooltip.astro";

<Tooltip term="nucleus" label="Nucleus" />
<Tooltip term="moquette" label="Moquette" />
```

- Import `Tooltip` on every content page that uses a glossary term.
- Prefer first useful occurrence per page (not every repeat).
- Always pass `label` for readable casing (default without label is UPPERCASE).
- Pages that import `Tooltip` and put terms inside tables must use HTML `<table>` —
  see `markdown-tables.md`.

## When to add a new term

Add a glossary entry when:

- A term appears on multiple pages
- The term has a specific meaning in this walkthrough
- First-time readers might confuse it (e.g. Moquette vs Mosquitto, client vs core)
