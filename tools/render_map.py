"""Refresh map.html with a new zone-state payload.

Inputs: a JSON file with the shape

    {
      "generated_at": "2026-06-17T20:50:00Z",
      "zones": [
        {"name": "East Legon", "lat": 5.6667, "lng": -0.1476,
         "state": "RAINING_LIGHT", "intensity_mm_hr": 0.4, "temp_c": 26.1},
        ...
      ]
    }

Output: rewrites map.html in place, replacing the `const PAYLOAD = {...};`
block between the markers below. Everything else in map.html stays untouched
so hand-edits to the styling/markup survive bot refreshes.

Usage:
    python tools/render_map.py path/to/state.json
    python tools/render_map.py -                 # read from stdin

Run from the repo root. Exit code 0 on success, 1 on missing markers / bad JSON.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_HTML = REPO_ROOT / "map.html"

# Markers delimit the regeneratable block — keep these comments in map.html.
_PAYLOAD_RE = re.compile(
    r"(// Generated payload — replace this block to refresh\. See tools/render_map\.py\.\n)"
    r"\s*const PAYLOAD = \{.*?\};",
    re.DOTALL,
)


def _format_payload(payload: dict) -> str:
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    return "const PAYLOAD = " + body + ";"


def render(state: dict) -> str:
    html = MAP_HTML.read_text(encoding="utf-8")
    if not _PAYLOAD_RE.search(html):
        raise SystemExit(
            "map.html is missing the PAYLOAD marker comment — refusing to refresh."
        )
    new_block = r"\1    " + _format_payload(state).replace("\n", "\n    ")
    return _PAYLOAD_RE.sub(new_block, html, count=1)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    src = argv[1]
    raw = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    state = json.loads(raw)
    if "zones" not in state or "generated_at" not in state:
        raise SystemExit("state JSON must have keys 'generated_at' and 'zones'.")
    MAP_HTML.write_text(render(state), encoding="utf-8")
    print(f"wrote {MAP_HTML} ({len(state['zones'])} zones)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
