"""Representasi state dan node pencarian.

Konvensi koordinat (SELURUH proyek): (baris, kolom), mulai dari 1,
baris 1 = paling atas, kolom 1 = paling kiri.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Optional


class State(NamedTuple):
    r: int        # baris (1-8)
    c: int        # kolom (1-8)
    status: int   # 0 = belum mengambil barang, 1 = sudah mengambil

    @property
    def cell(self) -> tuple[int, int]:
        return (self.r, self.c)


@dataclass
class Node:
    state: State
    parent: Optional["Node"] = None
    action: Optional[str] = None
    cost: int = 0      # g(n): biaya kumulatif dari initial state
    depth: int = 0     # jumlah aksi dari initial state
