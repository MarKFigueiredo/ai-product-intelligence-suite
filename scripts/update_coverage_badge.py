from __future__ import annotations

import json
from pathlib import Path

COVERAGE_JSON = Path("coverage.json")
BADGE_PATH = Path(".github/badges/coverage.svg")


def color_for(percent: float) -> str:
    if percent >= 90:
        return "#4c1"
    if percent >= 75:
        return "#97CA00"
    if percent >= 60:
        return "#dfb317"
    return "#e05d44"


def main() -> None:
    if not COVERAGE_JSON.exists():
        raise SystemExit("coverage.json not found. Run: python -m coverage json -o coverage.json")

    data = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    percent = float(data["totals"]["percent_covered_display"])

    label = "coverage"
    value = f"{percent:.0f}%"
    color = color_for(percent)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="104" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="61" height="20" fill="#555"/>
    <rect x="61" width="43" height="20" fill="{color}"/>
    <rect width="104" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="30.5" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="30.5" y="14">{label}</text>
    <text x="81.5" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="81.5" y="14">{value}</text>
  </g>
</svg>
'''
    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {BADGE_PATH} ({value})")


if __name__ == "__main__":
    main()
