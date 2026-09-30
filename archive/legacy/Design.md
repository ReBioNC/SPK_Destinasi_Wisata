# TravelFit — Design.md untuk Stitch

> Cara pakai: copy blok **MASTER PROMPT STITCH** di bawah (bagian dalam ```) lalu paste ke Stitch sebagai satu prompt. Hasilkan sebagai **mobile-responsive web app, Bahasa Indonesia**.
> Proyek asli: Django `TravelFit` — SPK rekomendasi destinasi wisata (CRISP-DM + K-Means + AHP + TOPSIS, validasi SAW + Spearman). Dataset 2.337 destinasi, 38 provinsi, 7 gugus pulau. 6 kriteria C1–C6.

---

## 1. Konteks singkat (jangan dihapus saat paste — Stitch butuh ini)

**TravelFit** membantu mahasiswa/backpacker memilih destinasi wisata Indonesia secara objektif, bukan sekadar ikut tren medsos atau cari yang termurah. User mengisi preferensi lengkap, sistem menimbang **6 kriteria bersamaan**:

- C1 Harga Tiket (cost) — sekaligus filter keras: di atas budget = tersaring
- C2 Rating Pengunjung 1–5 (benefit)
- C3 Jarak/Waktu Tempuh dari kota asal (cost, haversine)
- C4 Kelengkapan Fasilitas toilet/parkir/warung/mushola/penginapan (benefit)
- C5 Kesesuaian Kategori: 1 = kategori utama, 0.5 = sekunder, 0 = lain (benefit, bukan filter keras)
- C6 Kesesuaian Hobi via Jaccard Similarity (benefit)

Bobot dasar dari **AHP per profil** (semua CR < 0,1): **Hemat, Kualitas, Petualang, Seimbang**. User bisa ubah via slider sensitivity analysis. Ranking via **TOPSIS** (Vi = kedekatan ke solusi ideal, makin dekat 1 makin bagus). Tiap hasil wajib ada **explainability**: label cluster K-Means (mis. "Ekonomis", "Premium Berfasilitas Lengkap", "Rating Tinggi–Harga Menengah") + kalimat "Unggul pada …; tertahan oleh …" + breakdown per kriteria.

Halaman yang didesain: **(1) Landing + Form Preferensi, (2) Hasil Top-10 + Explainability penuh, (3) Peta Interaktif 38 provinsi, (4) Tentang/Metodologi**. Satu web scroll + navigasi tab, bukan 4 file terpisah.

---

## 2. MASTER PROMPT STITCH (COPY-PASTE MULAI DARI SINI)

```text
Build a playful Indonesian travel decision-support web app called "TravelFit — Cari Destinasi Wisata Terbaik", in Bahasa Indonesia, mobile-responsive.

VISUAL STYLE — "Playful Indonesian Archipelago":
- Background warm cream #FFFBEB with subtle doodle pattern (palm leaves, waves, temple outlines, very low opacity).
- Ink text #1E2A3B. Cards pure white with 2px ink border (#1E2A3B at 10% opacity), radius 20-28px, soft playful shadow (0 12px 32px rgba(30,42,59,.10)).
- Primary teal #0E9F8A for CTA and active states. Sunset orange #FF7A3D for highlights and rank #1-3 medals. Sunny yellow #FFC53D for badges and stars. Keep pink #FF7AB8, sky #5EA8FF, lilac #B79CFF only as small island/category accents.
- Typography: "Plus Jakarta Sans" for everything UI, ExtraBold for headings. Display headline with italic serif accent word (use Fraunces italic) in orange, e.g. "Liburan *paling pas* buat kantong dan hobimu."
- Sticker-style badges (rounded-full, thick border, slight rotate -2deg on hero badges). Wavy sunset divider between hero and form. Rounded-full pills for filters. Big chunky primary button (teal, white text, radius 16px, hover lift).
- Tone: friendly, youthful, backpacker/student. Use Bahasa Indonesia santai tapi jelas. Minimal emojis in UI (max 1 per heading).

GLOBAL NAVBAR (sticky, cream blur):
Left: logo mark "◈" in teal-orange gradient rounded square + "TravelFit" bold + small "SPK WISATA INDONESIA". Right links: Beranda, Hasil, Peta, Tentang + pill button "2.337 Destinasi • 38 Provinsi". Mobile: hamburger.

SECTION 1 — HERO (landing):
- Eyebrow pill: "● LIVE — 2.337 destinasi • 6 kriteria • AHP-TOPSIS" (yellow dot pulse).
- H1: "Liburan paling pas buat kantong dan hobimu." (words "paling pas" in orange italic serif).
- Sub: "TravelFit menimbang budget, rating, jarak, fasilitas, kategori, dan hobi kamu secara bersamaan — bukan cuma yang murah atau viral. Isi preferensi, pilih profil prioritas, dapatkan Top-10 + alasan tiap rekomendasi."
- 3 step stickers: "1. Isi preferensi" "2. Pilih profil" "3. Lihat Top-10 + alasannya" + link pill "atau pilih via Peta 🗺️".
- Stats row (4 mini cards): "2.337 Destinasi" / "38 Provinsi • 7 Pulau" / "6 Kriteria (C1-C6)" / "CR < 0,1 Teruji".
- Right side: playful illustration — stylized Indonesia islands map doodle with floating cards "Rating 4.8 ★", "Rp 15rb", "Cocok hiking!" and sun/cloud doodles. CTA buttons: primary "🔍 Cari Rekomendasi" (scroll to form), secondary "Lihat Peta".

SECTION 2 — FORM PREFERENSI (id="form", white card, 3 steps):
Title "Ceritakan liburan impianmu" + progress "Langkah 1/2/3".
- Group A "💰 Budget & Lokasi": Budget input with prefix "Rp" placeholder "250000" + helper "Di atas budget otomatis tersaring."; Kota asal dropdown (Jakarta, Bandung, Semarang, Surabaya, Yogyakarta, Medan, Makassar, Denpasar) helper "Menentukan jarak (C3)."; Wilayah tujuan dropdown provinsi (default "Daerah Istimewa Yogyakarta") helper "Bisa juga dipilih lewat Peta." Prefill example: Budget 150000, Kota asal Bandung, Wilayah DI Yogyakarta.
- Group B "🎯 Minat Kamu": Kategori utama dropdown (Alam, Budaya, Kuliner, Hiburan, Religi) + Kategori sekunder dropdown; Hobi checkbox chips multi-select (hiking, fotografi, kuliner lokal, snorkeling, sejarah, belanja, camping, bersepeda) — selected state teal fill. Helper: "Kategori & hobi TIDAK menyaring — jadi pembeda skor C5/C6."
- Group C "⚖️ Profil Prioritas" (radio cards 4 kolom): Hemat ("Budget paling menentukan", badge 38%, "Budget prioritas utama."), Kualitas ("Rating paling menentukan", "Pengalaman terbaik nomor satu."), Petualang ("Jarak paling menentukan", "Mudah dijangkau & sesuai hobi."), Seimbang — selected (highlight teal border, "Pilihan aman, semua seimbang."). Each card shows dominant criteria + percent.
- Collapsible "Analisis sensitivitas (ubah bobot manual, opsional)": 6 sliders C1 Harga, C2 Rating, C3 Jarak, C4 Fasilitas, C5 Kategori, C6 Hobi (0-100) with live % labels + note "Geser = pakai bobot kustom, bukan profil." + "Reset ke profil" link.
- Big submit "🔍 Cari Rekomendasi" full-width on mobile.
- Validation states: budget must be digits (accept "250.000" / "Rp 250000"), error message in red under field.

SECTION 3 — HASIL TOP-10 (id="hasil", show prefilled example state):
Header: "🏆 Top-10 Rekomendasi buat kamu" + sub "Wilayah DI Yogyakarta • Budget ≤ Rp 150.000 • Profil Seimbang • 42 kandidat tersaring" + buttons "Lihat di Peta 🗺️" + "Ubah Preferensi".
- Rank cards 1-10 vertical. Each card: left big medal circle (1 gold, 2 silver, 3 bronze, 4-10 teal outline), destination name bold (e.g. 1. Pantai Parangtritis, 2. Candi Prambanan, 3. Malioboro, 4. Hutan Pinus Mangunan, 5. Goa Pindul, 6. Candi Borobudur area Jogja, 7. Pantai Indrayanti, 8. Museum Ullen Sentalu, 9. Bukit Bintang, 10. Taman Sari), category + cluster sticker badges (e.g. "Alam" sky, "Ekonomis" yellow), price + rating line "Rp 10.000 | ★ 4.6", TOPSIS score bar (teal gradient, label "Skor 0.8742") full width 8px rounded.
- Explainability (WAJIB, jangan disingkat): quote box cream with "💡 Unggul pada Rating, Hobi; tertahan oleh Jarak." + 6 mini-bars C1-C6 with labels and values (Harga, Rating, Jarak, Fasilitas, Kategori, Hobi) showing proximity to ideal. Rank 1 expanded by default, ranks 2-10 collapsed with "Lihat alasan" expander.
- Empty state (hidden, show on logic): illustration + "Tidak ada destinasi yang cocok. Coba longgarkan budget atau pilih wilayah lain." + button "Reset Filter".
- Sort/filter row above list: chips "Semua" "Ekonomis" "Rating Tinggi" + sort dropdown "Skor tertinggi".

SECTION 4 — PETA INTERAKTIF (id="peta", sunset gradient card teal-to-navy):
Title "Jelajahi Nusantara dari Sabang sampai Merauke." + sub "38 provinsi • 7 gugus pulau. Klik pulau atau provinsi untuk isi otomatis Wilayah di form."
- Search input "Cari provinsi — mis. Jawa Barat, Bali, Papua…" + Reset + zoom +/- mock buttons.
- 7 island pills: Sumatera (yellow), Jawa (sky), Kalimantan (green), Sulawesi (pink), Bali-Nusa Tenggara (lilac), Maluku (red), Papua (cyan). Active = white fill.
- Center: STYLIZED Indonesia archipelago illustration (do NOT attempt accurate geo SVG — playful blobs per island group, dotted flight paths, sun + clouds). Overlay floating preview card on hover: province name, ibu kota, badge pulau.
- Bottom: legend dots + hint "Klik provinsi → tombol Pakai wilayah ini".
- Right/below: detail panel "Terpilih: Daerah Istimewa Yogyakarta — Pulau Jawa — Ibu kota Yogyakarta" + buttons "Pakai wilayah ini" (scrolls to form and fills wilayah) + "Hapus pilihan". + grid of 38 province chips (scrollable, 3 cols).
- If results exist, show dots on map for Top-10 with rank numbers.

SECTION 5 — TENTANG / METODOLOGI (id="tentang", white):
Title "Kenapa hasilnya bisa dipercaya?" + 4-step CRISP-DM timeline horizontal (Business → Data → Modeling K-Means + AHP-TOPSIS → Evaluation SAW+Spearman).
- 6 criteria table cards C1-C6 with Jenis badge (Cost red / Benefit green) + 1-line explanation.
- Formula strip (mono, cream boxes): "Vi = D-i / (D+i + D-i)" + "CR = CI/RI < 0,1" + "Jaccard = |A∩B|/|A∪B|".
- File bukti list: "Perhitungan_SPK_TravelFit.xlsx — 9 sheet AHP-TOPSIS" / "Dataset_Wisata_38_Provinsi.xlsx — 1.900 basis" / "README.md — rumus & alur".
- Team strip: 4 members (Kristofer Ryan Giggs 412024005 Ketua, Cristian Dion 412024006, Reynard Liu 412025022, Justin Augusto Liusri 412025029).
- Disclaimer small: "Hasil adalah bantuan keputusan, bukan keputusan final. Harga/rating/jarak dapat berubah."

FOOTER: "TravelFit — SPK Rekomendasi Destinasi Wisata (AHP-TOPSIS) • Tugas akademik" + links Beranda/Peta/Tentang.

INTERACTIONS: smooth scroll nav; profil card select updates slider defaults; slider input updates % live; "Pakai wilayah ini" fills form wilayah + toast "Wilayah terisi dari peta: X"; result card expander; sticky mobile CTA "Cari" at form bottom; hover lift on cards; count-up stats on load.

RESPONSIVE: desktop 12-col, form 3-col groups → mobile stacked; Top-10 2-col grid on desktop? keep 1-col list for readability; peta illustration full-width, detail panel below on mobile; font clamp h1 40-72px.

DO NOT: dark mode, accurate geographic SVG paths, backend logic, login/auth, payment, English copy, lorem ipsum — use real Indonesian dummy data above.
```
---

## 3. Catatan implementasi ke Django (setelah export dari Stitch)

Stitch hanya menghasilkan mockup statis. Saat memindahkan ke `recommender/templates/`:

1. Pecah per section: hero → `form_hasil.html` atas, hasil loop `{% for h in hasil %}` tetap pakai struktur kartu Stitch (medal, score bar `{% widthratio h.vi 1 100 %}`, badges `h.kategori` / `h.cluster`, `h.alasan` + 6 mini-bar dari `r.gap`).
2. Form field names WAJIB sama: `budget, kota_asal, wilayah, kategori_utama, kategori_sekunder, hobi, profil, sentuh_bobot, w1..w6`. Slider `onchange` set `sentuh_bobot=1`.
3. Peta: ganti ilustrasi playful Stitch dengan `index.html` / `nusantara.js` yang sudah akurat 38 provinsi bila butuh presisi; atau pertahankan ilustrasi Stitch untuk halaman marketing dan pakai peta akurat hanya di `/peta/`.
4. Warna sebagai CSS variables agarbiz dipakai ulang di `custom.css` + `nusantara.css`:
   `--cream:#FFFBEB; --ink:#1E2A3B; --teal:#0E9F8A; --sunset:#FF7A3D; --sun:#FFC53D;`
5. Copy Bahasa Indonesia di prompt sudah sesuai validasi `forms.py` (`parse_budget`, 8 kota asal, pesan kosong "Tidak ada destinasi yang cocok…").

## 4. Checklist sebelum paste ke Stitch

- [ ] Mode: standard / experimental + viewport desktop + mobile
- [ ] Bahasa: Indonesia (tulis eksplisit bila Stitch beralih ke Inggris)
- [ ] Iterasi 1: paste master prompt utuh → generate
- [ ] Iterasi 2 (bila perlu): "Perbanyak whitespace di hasil Top-10, buat mini-bar C1–C6 lebih ramping" atau "Buat peta lebih sederhana, fokus ke chips 38 provinsi"
- [ ] Export: download HTML / Figma, lalu adaptasi ke Django template tags

## 5. Contoh data dummy (sudah tertanam di prompt, untuk referensi)

Form terisi: Budget Rp 150.000, Bandung → DI Yogyakarta, Utama Alam, Sekunder Kuliner, Hobi hiking + fotografi, Profil Seimbang.
Top-10 (Vi menurun): Parangtritis 0.8742, Prambanan 0.8511, Malioboro 0.8304, Pinus Mangunan 0.8120, Goa Pindul 0.7955, dst. Cluster bervariasi: Ekonomis / Rating Tinggi–Harga Menengah / Premium Berfasilitas Lengkap.
