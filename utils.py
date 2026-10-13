"""Helper: format koordinat, tabel perbandingan, dan rendering grid HTML."""
from __future__ import annotations

import pandas as pd

from grid import OBSTACLES, PACKING, RACKS, SIZE, SLIPPERY, START
from search import SearchResult


def fmt(cell) -> str:
    return f"({cell[0]},{cell[1]})"


def path_text(res: SearchResult) -> str:
    return " → ".join(fmt(s.cell) + ("*" if s.status else "") for s in res.path_states)


def comparison_table(results: dict[str, SearchResult]) -> pd.DataFrame:
    best = min((r.cost for r in results.values() if r.found), default=None)
    rows = []
    for name, r in results.items():
        rows.append({
            "Metode": name,
            "Ditemukan": "Ya" if r.found else "Tidak",
            "Jumlah aksi": r.n_actions if r.found else "-",
            "Gerakan": r.n_moves if r.found else "-",
            "Total biaya": r.cost if r.found else "-",
            "Optimal biaya?": ("Ya" if r.cost == best else "Tidak") if r.found else "-",
            "Node diekspansi": r.expanded,
            "Node dibangkitkan": r.generated,
            "Frontier/stack maks": r.max_frontier,
            "Waktu (ms)": round(r.time_ms, 2),
        })
    return pd.DataFrame(rows)


# Warna
C = {
    "empty": "#f4f4f5", "S": "#22c55e", "R": "#fb923c", "P": "#ef4444",
    "X": "#3f3f46", "slip": "#bae6fd", "explored": "#e9d5ff",
    "path_pre": "#60a5fa", "path_post": "#facc15",
}


def grid_html(res: SearchResult | None = None, step: int = 0,
              show_explored: bool = False, show_slippery: bool = False) -> str:
    pre, post, explored = {}, {}, set()
    robot, robot_status = None, 0
    if res is not None and res.found:
        for i, s in enumerate(res.path_states[: step + 1]):
            (post if s.status else pre)[s.cell] = i
        cur = res.path_states[min(step, len(res.path_states) - 1)]
        robot, robot_status = cur.cell, cur.status
    if res is not None and show_explored:
        explored = {s.cell for s in res.expansion_order}

    css = ("<style>.wg{border-collapse:collapse;margin:auto}"
           ".wg td{width:58px;height:58px;text-align:center;font:600 15px sans-serif;"
           "border:2px solid #fff;border-radius:6px;color:#111}"
           ".wg th{font:600 13px sans-serif;color:#71717a;padding:2px}"
           ".sm{display:block;font-size:10px;font-weight:400;opacity:.7}</style>")
    h = [css, "<table class='wg'><tr><th></th>" +
         "".join(f"<th>{c}</th>" for c in range(1, SIZE + 1)) + "</tr>"]
    for r in range(1, SIZE + 1):
        h.append(f"<tr><th>{r}</th>")
        for c in range(1, SIZE + 1):
            cell = (r, c)
            bg, label, sub = C["empty"], "", ""
            if show_slippery and cell in SLIPPERY:
                bg = C["slip"]
            if cell in explored:
                bg = C["explored"]
            if cell in post:
                bg, sub = C["path_post"], f"#{post[cell]}"
            elif cell in pre:
                bg, sub = C["path_pre"], f"#{pre[cell]}"
            if cell in OBSTACLES:
                bg, label, sub = C["X"], "<span style='color:#fff'>X</span>", ""
            elif cell == START:
                bg, label = C["S"], "S"
            elif cell == PACKING:
                bg, label = C["P"], "P"
            elif cell in RACKS:
                bg, label = (C["R"] if cell not in pre and cell not in post else bg), "R"
            if cell == robot:
                label = "🤖" + ("📦" if robot_status else "")
            sm = f"<span class='sm'>{sub}</span>" if sub else ""
            h.append(f"<td style='background:{bg}'>{label}{sm}</td>")
        h.append("</tr>")
    h.append("</table>")
    return "".join(h)
