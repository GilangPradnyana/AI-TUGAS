"""Robot Gudang 8x8 - Visualisasi Uninformed Search (Streamlit).
Jalankan: streamlit run app.py
"""
import time

import streamlit as st

from grid import ORDERINGS, Warehouse
from search import METHODS, run_all
from utils import comparison_table, fmt, grid_html, path_text

st.set_page_config(page_title="Robot Gudang 8x8", page_icon="🤖", layout="wide")

DESKRIPSI = {
    "BFS": "Meluas level demi level dengan **Queue (FIFO)**. Menjamin solusi dengan **jumlah aksi paling sedikit**.",
    "DFS": "Masuk sedalam mungkin dengan **Stack (LIFO)**. Hemat memori, tetapi **tidak optimal**; jalur bergantung urutan tetangga.",
    "UCS": "Selalu memperluas node dengan **biaya kumulatif g(n) terkecil** (Priority Queue). Menjamin **biaya total termurah**.",
    "IDS": "**DFS berbatas kedalaman** yang dinaikkan bertahap (0,1,2,...). Optimal dalam jumlah aksi dan memori sangat kecil, tetapi mengekspansi ulang node.",
}


def status_text(res, step: int) -> str:
    aksi = "Posisi awal" if step == 0 else res.actions[step - 1]
    cur = res.path_states[step]
    return (f"**Langkah {step}/{res.n_actions}** · aksi: `{aksi}` · posisi: "
            f"`{fmt(cur.cell)}` · barang: {'✅ dibawa' if cur.status else '❌ belum'}")


# ---------------- Sidebar ----------------
st.sidebar.title("⚙️ Kontrol")
method = st.sidebar.selectbox("Metode pencarian", list(METHODS))
order_name = st.sidebar.selectbox("Urutan ekspansi tetangga", list(ORDERINGS))
variable_cost = st.sidebar.checkbox(
    "Biaya variabel (lantai licin = 4)", value=False,
    help="Jika aktif, UCS akan berbeda dari BFS karena memilih jalur berbiaya termurah.")
show_explored = st.sidebar.checkbox("Tampilkan sel yang diekspansi", value=False)

st.sidebar.markdown("---")
auto_anim = st.sidebar.checkbox("🎬 Animasi robot otomatis", value=True)
speed = st.sidebar.slider("Waktu per langkah (detik)", 0.05, 1.0, 0.30, 0.05)

c1, c2 = st.sidebar.columns(2)
run = c1.button("🔍 Cari Jalur", use_container_width=True)
reset = c2.button("♻️ Reset", use_container_width=True)
replay = st.sidebar.button("▶️ Putar ulang animasi", use_container_width=True)
compare = st.sidebar.button("📊 Bandingkan semua metode", use_container_width=True)

st.sidebar.markdown(f"**{method}**: {DESKRIPSI[method]}")
st.sidebar.markdown(
    "**Legenda**  \n🟩 S Start · 🟧 R Rak · 🟥 P Packing · ⬛ X Rintangan  \n"
    "🟦 jalur sebelum Ambil · 🟨 jalur setelah Ambil  \n"
    "🤖 robot · 📦 robot membawa barang  \n"
    "🟪 sel diekspansi · 🩵 lantai licin (mode biaya variabel)")

# ---------------- State ----------------
if reset:
    for k in ("result", "all_results", "animate", "run_id"):
        st.session_state.pop(k, None)
    st.rerun()

wh = Warehouse(variable_cost=variable_cost)
order = ORDERINGS[order_name]

if run:
    st.session_state["result"] = METHODS[method](wh, order)
    st.session_state["run_id"] = st.session_state.get("run_id", 0) + 1
    st.session_state["animate"] = auto_anim
if replay and "result" in st.session_state:
    st.session_state["animate"] = True
if compare:
    st.session_state["all_results"] = run_all(wh, order)

res = st.session_state.get("result")

# ---------------- Layout utama ----------------
st.title("🤖 Robot Gudang 8×8 — Uninformed Search")
st.caption("Start (1,1) → ambil barang di salah satu rak → antar ke Packing (8,8). "
           "Koordinat ditulis (baris, kolom).")

left, right = st.columns([3, 2])

# Kolom kanan ditulis lebih dulu agar hasil langsung tampil sementara animasi berjalan di kiri.
with right:
    st.subheader("Hasil")
    if res is None:
        st.info("Pilih metode lalu klik **Cari Jalur**.")
    elif not res.found:
        st.error("Tidak ditemukan solusi.")
    else:
        st.success(f"Solusi ditemukan oleh {res.method}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Jumlah aksi", res.n_actions)
        m2.metric("Total biaya", res.cost)
        m3.metric("Waktu", f"{res.time_ms:.2f} ms")
        m4, m5, m6 = st.columns(3)
        m4.metric("Node diekspansi", res.expanded)
        m5.metric("Frontier maks", res.max_frontier)
        m6.metric("Iterasi (IDS)", res.iterations if res.method == "IDS" else "-")
        st.markdown("**Urutan aksi**")
        st.code(" , ".join(res.actions), language=None)
        st.markdown("**Jalur koordinat** (tanda `*` = sudah membawa barang)")
        st.code(path_text(res), language=None)
        if res.method == "DFS":
            st.warning("DFS tidak menjamin jalur terpendek. Ganti urutan tetangga di sidebar "
                       "untuk melihat panjang jalur berubah.")
        if res.method == "IDS":
            st.caption("Jumlah node diekspansi besar karena IDS mengulang pencarian pada tiap batas kedalaman.")

with left:
    ctrl = st.container()
    status_ph = st.empty()
    grid_ph = st.empty()

    if res is None:
        grid_ph.markdown(grid_html(None, 0, False, variable_cost), unsafe_allow_html=True)
    elif not res.found:
        grid_ph.markdown(grid_html(res, 0, show_explored, variable_cost), unsafe_allow_html=True)
    elif st.session_state.pop("animate", False):
        # ---- Animasi: robot berjalan langkah demi langkah ----
        for i in range(res.n_actions + 1):
            status_ph.markdown("🎬 " + status_text(res, i))
            grid_ph.markdown(grid_html(res, i, show_explored, variable_cost),
                             unsafe_allow_html=True)
            time.sleep(speed)
        st.rerun()   # tampilkan slider manual pada posisi akhir
    else:
        with ctrl:
            step = st.slider("Langkah robot", 0, res.n_actions, res.n_actions,
                             key=f"step_{st.session_state.get('run_id', 0)}",
                             help="Geser untuk menelusuri jalur secara manual.")
        status_ph.markdown(status_text(res, step))
        grid_ph.markdown(grid_html(res, step, show_explored, variable_cost),
                         unsafe_allow_html=True)

all_res = st.session_state.get("all_results")
if all_res:
    st.subheader("📊 Perbandingan semua metode")
    st.dataframe(comparison_table(all_res), use_container_width=True, hide_index=True)
    st.caption(f"Urutan tetangga: {order_name} · Mode biaya: "
               f"{'variabel' if variable_cost else 'seragam'}. "
               "Ambil bernilai 1, jadi total biaya = jumlah gerakan + 1 pada mode seragam.")
