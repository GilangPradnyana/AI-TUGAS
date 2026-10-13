"""Uji sederhana: jalankan `python test_search.py`."""
from grid import OBSTACLES, ORDERINGS, RACKS, Warehouse
from search import METHODS, run_all


def validate(wh, res):
    assert res.found, f"{res.method} gagal menemukan solusi"
    st = res.path_states
    assert st[0] == wh.initial_state() and wh.is_goal(st[-1])
    assert "Ambil" in res.actions and res.actions.count("Ambil") == 1
    for a, b in zip(st, st[1:]):
        assert (a.r, a.c) not in OBSTACLES and (b.r, b.c) not in OBSTACLES
        assert abs(a.r - b.r) + abs(a.c - b.c) <= 1
    i = res.actions.index("Ambil")
    assert st[i].cell in RACKS            # Ambil dilakukan di rak


def main():
    for var in (False, True):
        wh = Warehouse(variable_cost=var)
        print(f"\n=== variable_cost={var} | state terjangkau={wh.reachable_state_count()} ===")
        for oname, order in ORDERINGS.items():
            out = run_all(wh, order)
            for r in out.values():
                validate(wh, r)
            costs = {k: v.cost for k, v in out.items()}
            # BFS optimal dalam jumlah aksi; UCS & (uniform) optimal dalam biaya
            assert out["BFS"].n_actions == out["IDS"].n_actions
            assert out["UCS"].cost <= min(v.cost for v in out.values())
            if not var:
                assert out["UCS"].cost == out["BFS"].cost == out["IDS"].cost == 15
            print(f"[{oname}] biaya={costs} aksi=" +
                  str({k: v.n_actions for k, v in out.items()}))
        out = run_all(wh)
        for k, v in out.items():
            print(f"  {k}: aksi={v.n_actions} biaya={v.cost} expanded={v.expanded} "
                  f"gen={v.generated} frontier={v.max_frontier} iter={v.iterations}")
    print("\nSemua uji lulus.")


if __name__ == "__main__":
    main()
