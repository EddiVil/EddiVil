import json
from pathlib import Path

CFG = Path("data/board.json")
OUT = Path("assets/tech-focus-map.svg")

def rect(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" ry="4" fill="{fill}"/>'

def main():
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    cols = int(cfg["cols"])
    grid = cfg["grid"]
    palette = cfg["palette"]
    cell = int(cfg.get("cell", 18))
    gap = int(cfg.get("gap", 4))

    rows = len(grid)
    width = cols * cell + (cols - 1) * gap + 20
    height = rows * cell + (rows - 1) * gap + 30

    # background is transparent; the cells themselves are visible on dark/light
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    svg.append('<g transform="translate(10,10)">')

    for r in range(rows):
        for c in range(cols):
            v = int(grid[r][c])
            v = max(0, min(v, len(palette) - 1))
            x = c * (cell + gap)
            y = r * (cell + gap)
            svg.append(rect(x, y, cell, cell, palette[v]))

    svg.append("</g>")
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated {OUT}")

if __name__ == "__main__":
    main()
