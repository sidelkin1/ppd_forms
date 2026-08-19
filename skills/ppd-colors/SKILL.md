---
name: ppd-colors
description: 'Enforce the PPD brand color palette from assets/цвета.pptx for all frontend work. Use when: creating or editing CSS, styling HTML/Jinja2 templates, picking colors in JavaScript, configuring group colors in YAML, or verifying/reviewing that existing frontend colors match the palette.'
argument-hint: 'Frontend: use only the PPD palette from цвета.pptx'
---

# PPD Frontend Color Palette

## When to Use

- Creating or editing any frontend file: CSS, HTML/Jinja2 templates, JavaScript, frontend YAML config
- Choosing a color for buttons, cards, headers, tables, badges, borders, group accents
- Reviewing or refactoring existing UI colors
- Any task that writes or changes a color value (hex / rgb)

## Rule

Use **only the 13 colors** from `assets/цвета.pptx` (the source of truth) for UI/design colors.
Do **not** introduce new brand/design colors.

Pure white `#FFFFFF` and black `#000000` — including their alpha variants (`rgba(...)`)
for shadows and hover overlays — are allowed as **functional** text/contrast colors only.

## Palette (from цвета.pptx)

| Hex | RGB | Usage hint |
|-----|-----|------------|
| `#F6D106` | 246, 209, 6 | Primary yellow — brand accent |
| `#F9BD27` | 249, 189, 39 | Golden yellow — headers, warnings, report cards |
| `#FA9D10` | 250, 157, 16 | Amber / orange |
| `#EF6B01` | 239, 107, 1 | Orange — secondary accent |
| `#C20937` | 194, 9, 55 | Crimson — danger, alerts |
| `#475B79` | 71, 91, 121 | Dark blue — group headers, tables |
| `#6985AF` | 105, 133, 175 | Medium blue |
| `#95A0B2` | 149, 160, 178 | Light blue-gray |
| `#3D464A` | 61, 70, 74 | Dark charcoal — dark backgrounds, footer |
| `#6B6B6B` | 107, 107, 107 | Gray — secondary headers |
| `#B2B2B2` | 178, 178, 178 | Light gray |
| `#BABABA` | 186, 186, 186 | Light gray |
| `#E2E2E2` | 226, 226, 226 | Very light gray — borders, subtle backgrounds |

### CSS custom properties (`--ppd-*`)

`app/static/css/main.css` defines one custom property per palette color in a `:root`
block. Prefer these variables instead of raw hex when writing CSS:

| Variable | Hex | RGB | Usage hint |
|----------|-----|-----|------------|
| `--ppd-yellow` | `#F6D106` | 246, 209, 6 | Primary yellow — brand accent |
| `--ppd-gold` | `#F9BD27` | 249, 189, 39 | Golden yellow — headers, warnings |
| `--ppd-amber` | `#FA9D10` | 250, 157, 16 | Amber / orange |
| `--ppd-orange` | `#EF6B01` | 239, 107, 1 | Orange — secondary accent |
| `--ppd-crimson` | `#C20937` | 194, 9, 55 | Crimson — danger, alerts |
| `--ppd-blue-dark` | `#475B79` | 71, 91, 121 | Dark blue — group headers, tables |
| `--ppd-blue` | `#6985AF` | 105, 133, 175 | Medium blue |
| `--ppd-blue-light` | `#95A0B2` | 149, 160, 178 | Light blue-gray |
| `--ppd-charcoal` | `#3D464A` | 61, 70, 74 | Dark charcoal — dark backgrounds, footer |
| `--ppd-gray` | `#6B6B6B` | 107, 107, 107 | Gray — secondary headers |
| `--ppd-gray-light` | `#B2B2B2` | 178, 178, 178 | Light gray |
| `--ppd-gray-lighter` | `#BABABA` | 186, 186, 186 | Light gray |
| `--ppd-gray-lightest` | `#E2E2E2` | 226, 226, 226 | Very light gray — borders, backgrounds |

Example:

```css
.card-header {
  background-color: var(--ppd-gold);
}
```

## How colors are used in this codebase

- `app/static/css/main.css` — defines all 13 palette colors as `--ppd-*` custom
  properties in a `:root` block, and uses them in Bootstrap overrides
  (`bg-dark` → `--ppd-charcoal`, `bg-warning` → `--ppd-gold`,
  `bg-danger` → `--ppd-crimson`)
- `app/api/config/yaml/reports.yaml` and `app/api/config/yaml/tables.yaml` — the
  `color:` field drives `--group-color` / `--header-bg` and must reference a `--ppd-*`
  variable (e.g. `color: 'var(--ppd-gold)'`), never a raw hex
- Templates read those via `var(--header-bg)` / `var(--group-color)`
  (see `app/templates/reports/macros/card.html`, `app/templates/tables/macros/card.html`)

## Procedure

1. Prefer existing palette-based classes, the `--ppd-*` custom properties from
   `main.css`, and the `--header-bg` / `--group-color` variables over hardcoded
   colors.
2. When a new color value is needed, pick it from the palette table above.
3. In CSS, write colors as uppercase 6-digit hex (e.g. `#F9BD27`), as `var(--ppd-*)`,
   or as `rgba()` of a palette color when transparency is required.
4. In YAML config and Jinja2 templates, reference colors as `var(--ppd-*)`
   (e.g. `color: 'var(--ppd-gold)'`) — never a raw hex.
5. Never hardcode a color outside the palette.
6. After frontend changes, run verification (below) and fix any violations.

## Verification

Run the bundled checker:

```bash
uv run python skills/ppd-colors/scripts/check_colors.py
```

It scans `app/static/css`, `app/templates`, and `app/api/config/yaml` for hex/rgb colors
and `var(--ppd-*)` references, listing any that are not in the palette or not a defined
`--ppd-*` variable (exit code `1` = violations found).

To scan additional paths, pass them as arguments:

```bash
uv run python skills/ppd-colors/scripts/check_colors.py app/static/javascript
```

## References

- Source of truth palette: [цвета.pptx](./assets/цвета.pptx)
- Checker script: [check_colors.py](./scripts/check_colors.py)
