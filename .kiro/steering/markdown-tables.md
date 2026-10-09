---
inclusion: always
---

# Markdown tables

## Pipe tables (plain MDX)

GFM tables need a header row, a separator row (`| --- | --- |`), and consistent
column counts. Do not put unescaped `|` inside cells.

After editing Markdown, rely on `.kiro/hooks/format-md-tables.py` (wired via
`format-markdown-tables.json`) rather than hand-fixing separator rows in a rush.

Prefer simple two- or three-column tables for BOM, cost, and CLI flag summaries.

## HTML tables (when Tooltip is imported)

Markdown pipe tables do not render reliably in `.mdx` files that import custom
components such as `Tooltip` — the MDX parser can treat the pipes as text.

- Plain `.mdx` with no component imports → Markdown pipe tables are fine.
- Page that imports `Tooltip` (or puts components inside a table) → use HTML `<table>`.

```mdx
<table>
  <thead>
    <tr>
      <th>Role</th>
      <th>Hardware</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <Tooltip term="core-device" label="Core device" />
      </td>
      <td>
        <Tooltip term="nuc6cay" label="Intel NUC6CAY" />
      </td>
    </tr>
  </tbody>
</table>
```
