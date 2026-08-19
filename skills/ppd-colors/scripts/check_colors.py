"""Verify frontend colors against the PPD brand palette.

Usage:
    uv run python skills/ppd-colors/scripts/check_colors.py [paths...]

Scans CSS, HTML/Jinja2, YAML, and JS files (default roots: app/static/css,
app/templates, app/api/config/yaml) and reports any hex/rgb color that is NOT
part of the PPD palette defined in skills/ppd-colors/SKILL.md (source of truth:
skills/ppd-colors/assets/цвета.pptx).

Rules implemented here match SKILL.md:
  - All UI/design colors must be one of the 13 palette colors.
  - Pure white (#FFFFFF) and black (#000000), including rgba() alpha variants,
    are allowed as functional text/contrast/shadow colors.

Exclusions:
  - Vendored libraries (paths containing "bootstrap")
  - Minified assets (*.min.css, *.min.js)

Exit code: 0 = all colors are in-palette, 1 = violations found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# The 13 palette colors from assets/цвета.pptx (uppercase, 6-digit RGB).
PALETTE = {
    "F6D106",
    "EF6B01",
    "FA9D10",
    "F9BD27",
    "C20937",
    "475B79",
    "6985AF",
    "95A0B2",
    "3D464A",
    "6B6B6B",
    "B2B2B2",
    "BABABA",
    "E2E2E2",
}

# Functional neutrals allowed as text/contrast/shadow colors only.
ALLOWED_NEUTRALS = {"000000", "FFFFFF"}

# The --ppd-* custom properties defined in app/static/css/main.css :root.
PPD_VARS = {
    "--ppd-yellow",
    "--ppd-gold",
    "--ppd-amber",
    "--ppd-orange",
    "--ppd-crimson",
    "--ppd-blue-dark",
    "--ppd-blue",
    "--ppd-blue-light",
    "--ppd-charcoal",
    "--ppd-gray",
    "--ppd-gray-light",
    "--ppd-gray-lighter",
    "--ppd-gray-lightest",
}

DEFAULT_ROOTS = [
    Path("app/static/css"),
    Path("app/templates"),
    Path("app/api/config/yaml"),
]

EXTENSIONS = {".css", ".html", ".htm", ".yaml", ".yml", ".js"}
SKIP_PARTS = ("bootstrap",)
SKIP_SUFFIXES = (".min.css", ".min.js")

HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(
    r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})"
    r"(?:\s*,\s*[\d.]+)?\s*\)"
)
VAR_RE = re.compile(r"var\(\s*(--ppd-[\w-]+)\s*\)")


def normalize_hex(value: str) -> str | None:
    """Return a 6-digit uppercase RGB string from a hex color, or None."""
    h = value.lstrip("#")
    if len(h) in (3, 4):  # shorthand / shorthand-with-alpha
        h = "".join(ch * 2 for ch in h)
    if len(h) in (6, 8):  # full / full-with-alpha
        return h[:6].upper()
    return None


def collect_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            print(f"SKIP (missing): {root}")
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in EXTENSIONS:
                continue
            if any(part.lower() in SKIP_PARTS for part in path.parts):
                continue
            if path.name.lower().endswith(SKIP_SUFFIXES):
                continue
            files.append(path)
    return files


def check_hex(value: str) -> str | None:
    """Return a violation message for a hex color outside the palette."""
    rgb = normalize_hex(value)
    if rgb and rgb not in PALETTE and rgb not in ALLOWED_NEUTRALS:
        return f"{value} -> RGB {rgb}"
    return None


def check_rgb(match: re.Match[str]) -> str | None:
    """Return a violation message for an rgb() color outside the palette."""
    r, g, b = (int(match.group(i)) for i in (1, 2, 3))
    if not all(0 <= c <= 255 for c in (r, g, b)):
        return None
    rgb = f"{r:02X}{g:02X}{b:02X}"
    if rgb not in PALETTE and rgb not in ALLOWED_NEUTRALS:
        return f"rgb({r}, {g}, {b}) -> RGB {rgb}"
    return None


def scan_text(text: str, path: Path) -> list[str]:
    """Find out-of-palette colors in a file's text."""
    found: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for value in HEX_RE.findall(line):
            message = check_hex(value)
            if message:
                found.append(f"{path}:{lineno}: {message}")
        for match in RGB_RE.finditer(line):
            message = check_rgb(match)
            if message:
                found.append(f"{path}:{lineno}: {message}")
        for match in VAR_RE.finditer(line):
            name = match.group(1)
            if name not in PPD_VARS:
                msg = f"var({name}) is not a defined --ppd-* variable"
                found.append(f"{path}:{lineno}: {msg}")
    return found


def main(argv: list[str]) -> int:
    roots = [Path(p) for p in argv] if argv else DEFAULT_ROOTS
    files = collect_files(roots)
    violations: list[str] = []

    for path in sorted(files):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        violations.extend(scan_text(text, path))

    print(f"Checked {len(files)} file(s).")
    if violations:
        print(f"Found {len(violations)} color(s) outside the PPD palette:")
        for v in violations:
            print(f"  {v}")
        return 1
    print("OK: all colors are in the PPD palette.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
