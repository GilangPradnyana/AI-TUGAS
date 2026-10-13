# BRIEF KONSEP LENGKAP
## Sistem Robot Gudang 8×8 berbasis Uninformed Search
### dengan Visualisasi Web menggunakan Python (Streamlit)

---

**Versi Dokumen**     : 1.0  
**Tanggal**            : 12 Oktober 2026  
**Konteks**            : Materi Artificial Intelligence – Problem Space & Blind Search  
**Tujuan Dokumen**     : Menjadi acuan lengkap dari perumusan masalah hingga development sistem

---

## 1. Latar Belakang

Dalam kecerdasan buatan, banyak permasalahan dapat diselesaikan dengan pendekatan **pencarian (search)**. Sebelum algoritma yang lebih canggih (heuristic search) digunakan, fondasi yang harus dikuasai adalah **Uninformed Search** atau **Pencarian Buta**.

Sistem Robot Gudang ini dibuat untuk menerapkan konsep tersebut secara nyata. Robot harus:
- Bergerak di dalam gudang berbentuk grid 8×8,
- Mengambil barang dari salah satu rak,
- Mengantarnya ke area packing,
- Menghindari rintangan,
- Dengan menggunakan metode pencarian buta (BFS, DFS, UCS, dan IDS).

Tujuan utamanya adalah agar mahasiswa/pengguna memahami:
1. Bagaimana merumuskan masalah menjadi **Problem Space**,
2. Bagaimana algoritma pencarian buta bekerja,
3. Bagaimana membandingkan kelebihan dan kekurangan masing-masing metode,
4. Bagaimana mengimplementasikan dan memvisualisasikannya secara interaktif.

---

## 2. Tujuan Sistem

### Tujuan Umum
Membangun sistem pencarian jalur robot gudang yang interaktif berbasis web dengan menggunakan metode Uninformed Search.

### Tujuan Khusus
1. Merumuskan masalah robot gudang secara formal (State, Initial State, Goal Test, Actions, Path Cost).
2. Mengimplementasikan empat metode pencarian buta: **BFS, DFS, UCS, dan IDS**.
3. Menampilkan proses pencarian dan jalur solusi secara visual di web.
4. Memberikan perbandingan kinerja antar metode (jumlah langkah, biaya, dan karakteristik).
5. Menyediakan antarmuka yang mudah digunakan untuk keperluan pembelajaran.

---

## 3. Ruang Lingkup

### Yang Termasuk
- Grid gudang berukuran **8×8**
- Beberapa rak barang (multi-rack, cukup ambil satu)
- Area packing sebagai tujuan akhir
- Rintangan (obstacle)
- Metode: BFS, DFS, UCS, IDS
- Visualisasi web interaktif
- Tabel perbandingan hasil

### Yang Tidak Termasuk (Out of Scope)
- Heuristic Search (A*, Greedy, dll)
- Multi-agent (lebih dari satu robot)
- Dinamika real-time (barang bergerak, robot lain)
- Optimasi dengan machine learning

---

## 4. Formulasi Masalah (Problem Formulation)

Ini adalah bagian paling penting sesuai materi kuliah.

| Komponen          | Nilai / Penjelasan                                      |
|-------------------|---------------------------------------------------------|
| **State**         | `(x, y, status)` <br> x, y = koordinat 1–8 <br> status = 0 (belum ambil) / 1 (sudah ambil) |
| **Initial State** | `(1, 1, 0)`                                             |
| **Goal State**    | `(8, 8, 1)`                                             |
| **Actions**       | `Move(Atas)`, `Move(Bawah)`, `Move(Kiri)`, `Move(Kanan)`, `Ambil` |
| **Transition**    | Posisi berubah sesuai aksi, status berubah menjadi 1 hanya jika berada di rak dan melakukan Ambil |
| **Path Cost**     | Setiap aksi bergerak = 1                                |
| **Constraints**   | Tidak boleh keluar grid, tidak boleh masuk sel rintangan (X) |

**Catatan Multi-Rak:**  
Robot cukup mengambil dari **salah satu rak saja**. Algoritma akan secara otomatis memilih rak yang paling menguntungkan sesuai strategi pencariannya.

---

## 5. Layout Gudang 8×8

### Posisi Penting
- **S (Start)**     : (1,1)
- **R (Rak)**       : (2,3), (2,6), (5,3), (5,5), (8,2)
- **P (Packing)**   : (8,8)
- **X (Rintangan)** : (1,4), (1,7), (3,2), (3,5), (3,8), (4,1), (4,4), (4,7), (5,6), (6,2), (6,7), (8,4)

### Representasi Visual (Teks)

```
     1    2    3    4    5    6    7    8
  ┌────┬────┬────┬────┬────┬────┬────┬────┐
1 │ S  │    │    │ X  │    │    │ X  │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
2 │    │    │ R  │    │    │ R  │    │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
3 │    │ X  │    │    │ X  │    │    │ X  │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
4 │ X  │    │    │ X  │    │    │ X  │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
5 │    │    │ R  │    │ R  │ X  │    │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
6 │    │ X  │    │    │    │    │ X  │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
7 │    │    │    │    │    │    │    │    │
  ├────┼────┼────┼────┼────┼────┼────┼────┤
8 │    │ R  │    │ X  │    │    │    │ P  │
  └────┴────┴────┴────┴────┴────┴────┴────┘
```

---

## 6. Metode Pencarian yang Digunakan

| Metode | Strategi                    | Struktur Data      | Sifat Hasil              | Cocok untuk Kasus Ini? |
|--------|-----------------------------|--------------------|--------------------------|------------------------|
| **BFS**   | Level demi level           | Queue             | Jalur terpendek         | Sangat Cocok          |
| **DFS**   | Sedalam mungkin            | Stack             | Satu jalur (sering panjang) | Kurang Cocok       |
| **UCS**   | Biaya kumulatif terkecil   | Priority Queue    | Jalur termurah          | Cocok (sama BFS jika cost=1) |
| **IDS**   | DLS berulang               | Stack + iterasi   | Jalur terpendek + hemat memori | Sangat Direkomendasikan |

---

## 7. Arsitektur Sistem

```
┌──────────────────────────────────────────────────────┐
│                    WEB INTERFACE                     │
│                   (Streamlit)                        │
│  • Pilih metode pencarian                            │
│  • Tombol "Cari Jalur"                               │
│  • Visualisasi Grid 8×8 berwarna                     │
│  • Animasi / highlight jalur solusi                  │
│  • Tabel hasil & perbandingan                        │
└──────────────────────────┬───────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────┐
│                   PYTHON BACKEND                     │
│  • grid.py      → Definisi layout & validasi gerak   │
│  • state.py     → Representasi state                 │
│  • search.py    → BFS, DFS, UCS, IDS                 │
│  • utils.py     → Rekonstruksi jalur & metrik        │
│  • app.py       → Antarmuka Streamlit                │
└──────────────────────────────────────────────────────┘
```

---

## 8. Tech Stack

| Komponen              | Teknologi              | Alasan |
|-----------------------|------------------------|--------|
| Bahasa Pemrograman    | Python 3.10+           | Mudah, banyak library AI & visualisasi |
| Web Framework         | **Streamlit**          | Paling cepat untuk prototype interaktif + visualisasi |
| Struktur Data         | `queue.Queue`, `heapq`, `list` | Standar untuk BFS, UCS, DFS |
| Visualisasi Grid      | Streamlit + HTML/CSS atau `st.dataframe` + pewarnaan | Mudah diintegrasikan |
| Dependency Management | `requirements.txt`     | Reproducible |

**Alternatif** (jika ingin lebih fleksibel):
- Flask / FastAPI + HTML Canvas + JavaScript

---

## 9. Struktur File Proyek

```
robot_gudang/
│
├── app.py                 # Main Streamlit application
├── grid.py                # Layout gudang, obstacle, valid move
├── state.py               # Class State
├── search.py              # Implementasi BFS, DFS, UCS, IDS
├── utils.py               # Helper functions (path, metrics)
├── requirements.txt       # streamlit, dll
└── README.md              # Cara menjalankan
```

---

## 10. Alur Development (Tahapan Pengerjaan)

### Tahap 1: Problem Formulation & Layout
- Definisikan state representation
- Buat layout 8×8 beserta posisi S, R, P, X
- Validasi gerakan (tidak keluar grid & tidak masuk obstacle)

### Tahap 2: Core Search Algorithms
- Implementasi BFS
- Implementasi DFS
- Implementasi UCS
- Implementasi IDS
- Fungsi rekonstruksi jalur dari parent pointer

### Tahap 3: Metrics & Comparison
- Hitung jumlah langkah
- Hitung total biaya
- Simpan urutan ekspansi (opsional)
- Buat fungsi perbandingan antar metode

### Tahap 4: Web Interface (Streamlit)
- Sidebar: pilihan metode + tombol jalankan
- Area utama: visualisasi grid berwarna
- Highlight jalur solusi
- Tampilkan tabel hasil
- Tampilkan penjelasan singkat metode yang dipilih

### Tahap 5: Testing & Polish
- Uji semua metode
- Pastikan jalur valid (tidak menabrak X)
- Perbaiki edge case (tidak ada jalur, dll)
- Tambahkan legenda dan petunjuk penggunaan

---

## 11. Fitur yang Akan Muncul di Web

1. **Grid Interaktif Berwarna**
   - S = Hijau
   - R = Oranye
   - P = Merah
   - X = Abu-abu gelap
   - Jalur solusi = Kuning / Biru

2. **Kontrol**
   - Dropdown pilihan metode (BFS / DFS / UCS / IDS)
   - Tombol “Cari Jalur”
   - Tombol “Reset”

3. **Hasil**
   - Jumlah langkah
   - Total biaya
   - Waktu eksekusi (opsional)
   - Urutan koordinat jalur
   - Status: “Solusi ditemukan” / “Tidak ditemukan”

4. **Perbandingan**
   - Tabel ringkas hasil semua metode

---

## 12. Contoh Hasil yang Diharapkan

| Metode | Jumlah Langkah | Biaya | Optimal? | Keterangan |
|--------|----------------|-------|----------|----------|
| BFS    | 14             | 14    | Ya       | Solusi terdangkal |
| DFS    | 22–28          | 22–28 | Tidak    | Bergantung urutan tetangga |
| UCS    | 14             | 14    | Ya       | Sama dengan BFS (cost seragam) |
| IDS    | 14             | 14    | Ya       | Optimal + hemat memori |

---

## 13. Manfaat Sistem

- Memperkuat pemahaman konsep **Problem Space**
- Memperlihatkan perbedaan perilaku BFS, DFS, UCS, dan IDS secara visual
- Menjadi media pembelajaran interaktif
- Dapat dikembangkan lebih lanjut menjadi heuristic search (A*)

---

## 14. Rencana Pengembangan Selanjutnya (Future Work)

1. Menambahkan cost yang berbeda-beda (agar UCS berbeda hasilnya)
2. Multi-pickup (wajib mengambil lebih dari satu rak)
3. Animasi pergerakan robot langkah demi langkah
4. Mode “Step-by-step” (tampilkan frontier satu per satu)
5. Implementasi A* sebagai perbandingan dengan informed search

---

## 15. Kesimpulan

Sistem Robot Gudang 8×8 ini dirancang sebagai penerapan praktis dari materi **Konsep Masalah, Ruang Masalah, dan Pencarian Buta**.  

Dengan menggabungkan:
- Formulasi masalah yang benar,
- Implementasi empat metode uninformed search,
- Visualisasi web interaktif menggunakan Streamlit,


---
