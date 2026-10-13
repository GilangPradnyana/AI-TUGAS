"""Empat algoritma Uninformed Search: BFS, DFS, UCS, IDS.

Semua fungsi memakai antarmuka sama dan mengembalikan SearchResult.
BFS/DFS/UCS memakai explored set (graph search) agar tidak berputar.
IDS memakai pengecekan siklus pada jalur saat ini (tanpa explored set global,
sehingga tetap hemat memori).
"""
from __future__ import annotations

import heapq
import itertools
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from grid import Warehouse
from state import Node, State


@dataclass
class SearchResult:
    method: str
    found: bool
    path_states: list = field(default_factory=list)   # list[State]
    actions: list = field(default_factory=list)       # list[str]
    cost: int = 0
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    time_ms: float = 0.0
    expansion_order: list = field(default_factory=list)  # list[State]
    iterations: int = 1       # hanya relevan untuk IDS
    note: str = ""

    @property
    def n_actions(self) -> int:
        return len(self.actions)

    @property
    def n_moves(self) -> int:
        return sum(1 for a in self.actions if a != "Ambil")


def _reconstruct(node: Node):
    states, actions = [], []
    while node is not None:
        states.append(node.state)
        if node.action:
            actions.append(node.action)
        node = node.parent
    states.reverse()
    actions.reverse()
    return states, actions


def _finish(res: SearchResult, node: Optional[Node], t0: float) -> SearchResult:
    res.time_ms = (time.perf_counter() - t0) * 1000
    if node is not None:
        res.found = True
        res.path_states, res.actions = _reconstruct(node)
        res.cost = node.cost
    return res


# --------------------------------------------------------------------------
def bfs(wh: Warehouse, order=None) -> SearchResult:
    t0 = time.perf_counter()
    res = SearchResult("BFS", False)
    start = Node(wh.initial_state())
    frontier = deque([start])          # Queue FIFO
    seen = {start.state}
    res.generated = 1
    while frontier:
        res.max_frontier = max(res.max_frontier, len(frontier))
        node = frontier.popleft()
        res.expanded += 1
        res.expansion_order.append(node.state)
        if wh.is_goal(node.state):
            return _finish(res, node, t0)
        for act, nxt, c in wh.successors(node.state, order):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(Node(nxt, node, act, node.cost + c, node.depth + 1))
                res.generated += 1
    return _finish(res, None, t0)


def dfs(wh: Warehouse, order=None) -> SearchResult:
    t0 = time.perf_counter()
    res = SearchResult("DFS", False)
    stack = [Node(wh.initial_state())]   # Stack LIFO
    explored: set[State] = set()
    res.generated = 1
    while stack:
        res.max_frontier = max(res.max_frontier, len(stack))
        node = stack.pop()
        if node.state in explored:
            continue
        explored.add(node.state)
        res.expanded += 1
        res.expansion_order.append(node.state)
        if wh.is_goal(node.state):
            return _finish(res, node, t0)
        # dibalik agar tetangga pertama pada urutan ekspansi dikunjungi lebih dulu
        for act, nxt, c in reversed(wh.successors(node.state, order)):
            if nxt not in explored:
                stack.append(Node(nxt, node, act, node.cost + c, node.depth + 1))
                res.generated += 1
    return _finish(res, None, t0)


def ucs(wh: Warehouse, order=None) -> SearchResult:
    t0 = time.perf_counter()
    res = SearchResult("UCS", False)
    counter = itertools.count()          # tie-breaker FIFO untuk biaya sama
    start = Node(wh.initial_state())
    heap = [(0, next(counter), start)]   # Priority Queue berdasarkan g(n)
    best = {start.state: 0}
    explored: set[State] = set()
    res.generated = 1
    while heap:
        res.max_frontier = max(res.max_frontier, len(heap))
        g, _, node = heapq.heappop(heap)
        if node.state in explored:
            continue                      # entri usang
        explored.add(node.state)
        res.expanded += 1
        res.expansion_order.append(node.state)
        if wh.is_goal(node.state):        # goal test saat DIEKSPANSI (wajib untuk UCS)
            return _finish(res, node, t0)
        for act, nxt, c in wh.successors(node.state, order):
            ng = g + c
            if nxt not in explored and ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                heapq.heappush(heap, (ng, next(counter),
                                      Node(nxt, node, act, ng, node.depth + 1)))
                res.generated += 1
    return _finish(res, None, t0)


def ids(wh: Warehouse, order=None, max_limit: int = 200) -> SearchResult:
    t0 = time.perf_counter()
    res = SearchResult("IDS", False)
    last_order: list = []

    def dls(node: Node, limit: int, on_path: set, trace: list):
        """Depth-Limited Search. Return (node_solusi | None, terpotong?)."""
        res.expanded += 1
        trace.append(node.state)
        res.max_frontier = max(res.max_frontier, node.depth + 1)  # kedalaman stack
        if wh.is_goal(node.state):
            return node, False
        if node.depth == limit:
            return None, True
        cutoff = False
        for act, nxt, c in wh.successors(node.state, order):
            if nxt in on_path:            # cek siklus pada jalur saat ini
                continue
            res.generated += 1
            on_path.add(nxt)
            child = Node(nxt, node, act, node.cost + c, node.depth + 1)
            sol, cut = dls(child, limit, on_path, trace)
            on_path.discard(nxt)
            if sol is not None:
                return sol, False
            cutoff = cutoff or cut
        return None, cutoff

    start = Node(wh.initial_state())
    res.generated = 1
    for limit in range(max_limit + 1):
        res.iterations = limit + 1
        trace: list = []
        sol, cutoff = dls(start, limit, {start.state}, trace)
        last_order = trace
        if sol is not None:
            res.expansion_order = last_order
            return _finish(res, sol, t0)
        if not cutoff:        # seluruh ruang sudah habis ditelusuri -> tidak ada solusi
            break
    res.expansion_order = last_order
    return _finish(res, None, t0)


METHODS = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "IDS": ids}


def run_all(wh: Warehouse, order=None) -> dict[str, SearchResult]:
    return {name: fn(wh, order) for name, fn in METHODS.items()}
