"""Definisi gudang 8x8, aturan gerak, dan fungsi transisi."""
from __future__ import annotations

from state import State

SIZE = 8
START = (1, 1)
PACKING = (8, 8)
RACKS = {(2, 3), (2, 6), (5, 3), (5, 5), (8, 2)}
OBSTACLES = {
    (1, 4), (1, 7), (3, 2), (3, 5), (3, 8), (4, 1),
    (4, 4), (4, 7), (5, 6), (6, 2), (6, 7), (8, 4),
}

# Sel "lantai licin": hanya aktif pada mode biaya variabel (membuat UCS != BFS).
# Biaya MASUK ke sel licin = SLIPPERY_COST, sel biasa = 1.
SLIPPERY = {(7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (4, 3), (5, 4)}
SLIPPERY_COST = 4

# Biaya aksi Ambil (dinyatakan eksplisit, sesuai revisi brief v2.0).
AMBIL_COST = 1

MOVES = {
    "Atas": (-1, 0),
    "Bawah": (1, 0),
    "Kiri": (0, -1),
    "Kanan": (0, 1),
}

# Urutan ekspansi tetangga (menentukan jalur DFS & tie-break lainnya).
ORDERINGS = {
    "Atas, Bawah, Kiri, Kanan": ["Atas", "Bawah", "Kiri", "Kanan"],
    "Kanan, Bawah, Kiri, Atas": ["Kanan", "Bawah", "Kiri", "Atas"],
    "Bawah, Kanan, Atas, Kiri": ["Bawah", "Kanan", "Atas", "Kiri"],
    "Kiri, Atas, Bawah, Kanan": ["Kiri", "Atas", "Bawah", "Kanan"],
}
DEFAULT_ORDER = ORDERINGS["Atas, Bawah, Kiri, Kanan"]


class Warehouse:
    def __init__(self, variable_cost: bool = False):
        self.variable_cost = variable_cost
        self.start = State(*START, 0)
        self.goal_cell = PACKING

    # ---- validasi -------------------------------------------------------
    @staticmethod
    def in_grid(r: int, c: int) -> bool:
        return 1 <= r <= SIZE and 1 <= c <= SIZE

    def is_free(self, r: int, c: int) -> bool:
        return self.in_grid(r, c) and (r, c) not in OBSTACLES

    def move_cost(self, cell: tuple[int, int]) -> int:
        if self.variable_cost and cell in SLIPPERY:
            return SLIPPERY_COST
        return 1

    # ---- problem formulation -------------------------------------------
    def initial_state(self) -> State:
        return self.start

    def is_goal(self, s: State) -> bool:
        return s.cell == self.goal_cell and s.status == 1

    def successors(self, s: State, order=None):
        """Menghasilkan list (nama_aksi, state_baru, biaya_aksi)."""
        order = order or DEFAULT_ORDER
        result = []
        for name in order:
            dr, dc = MOVES[name]
            nr, nc = s.r + dr, s.c + dc
            if self.is_free(nr, nc):
                result.append((name, State(nr, nc, s.status), self.move_cost((nr, nc))))
        # Ambil: hanya di rak dan status masih 0
        if s.status == 0 and s.cell in RACKS:
            result.append(("Ambil", State(s.r, s.c, 1), AMBIL_COST))
        return result

    def reachable_state_count(self) -> int:
        """Jumlah state yang dapat dicapai (untuk informasi/validasi)."""
        seen, stack = {self.start}, [self.start]
        while stack:
            cur = stack.pop()
            for _, nxt, _ in self.successors(cur):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return len(seen)
