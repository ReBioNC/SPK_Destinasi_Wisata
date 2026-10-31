import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
OUT = sys.argv[1]
plt.rcParams["font.family"] = "Times New Roman"
INK, TEAL, SOFT, MUTED = "#1f2d2b", "#1f5c55", "#e3efeb", "#5b6b68"

def box(ax, x, y, w, h, title, body, fc=SOFT):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=TEAL, lw=1.4))
    ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top", fontsize=11.5, weight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.48, body, ha="center", va="top", fontsize=9.5, color=INK, linespacing=1.35)

def arrow(ax, a, b, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, lw=1.4, color=TEAL, **kw))

# Gambar 1: tahapan pelaksanaan
fig, ax = plt.subplots(figsize=(8.6, 3.5)); ax.set_xlim(0, 9); ax.set_ylim(0.3, 3.75); ax.axis("off")
steps = [("1. Pengumpulan Data", "Kaggle 437 + kurasi 6\nkuesioner bobot kriteria"),
         ("2. Persiapan Data", "cleaning, flag kualitas,\nfitur C1–C6, manifest hash"),
         ("3. Segmentasi K-Means", "k = 2–6, k-means++,\nseed 42, silhouette"),
         ("4. AHP dan TOPSIS", "bobot dari kuesioner (CR),\nperingkat kedekatan ideal"),
         ("5. Konstruksi Aplikasi", "Django, peta provinsi,\npenjelasan per kriteria"),
         ("6. Pengujian", "uji otomatis, SAW–Spearman,\nsensitivitas, uji pengguna")]
w, h = 2.55, 1.05
pos = [(0.25, 2.55), (3.22, 2.55), (6.19, 2.55), (6.19, 0.55), (3.22, 0.55), (0.25, 0.55)]
for (t, b), (x, y) in zip(steps, pos): box(ax, x, y, w, h, t, b)
arrow(ax, (2.82, 3.07), (3.2, 3.07)); arrow(ax, (5.79, 3.07), (6.17, 3.07))
arrow(ax, (7.46, 2.53), (7.46, 1.62)); arrow(ax, (6.17, 1.07), (5.79, 1.07)); arrow(ax, (3.2, 1.07), (2.82, 1.07))
arrow(ax, (1.52, 1.62), (1.52, 2.53), linestyle="--")
ax.text(1.62, 2.07, "umpan balik", fontsize=9, color=MUTED, style="italic", va="center")
fig.savefig(f"{OUT}/gambar1_tahapan.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# Gambar 2: arsitektur sistem
fig, ax = plt.subplots(figsize=(8.6, 4.6)); ax.set_xlim(0, 9.2); ax.set_ylim(0, 5); ax.axis("off")
ax.text(0.2, 4.78, "Luring (pengembang)", fontsize=11, weight="bold", color=MUTED)
ax.text(5.05, 4.78, "Daring (pengguna)", fontsize=11, weight="bold", color=MUTED)
ax.plot([4.85, 4.85], [0.2, 4.85], ls=":", color=MUTED, lw=1)
box(ax, 0.2, 3.3, 4.3, 1.25, "Sumber data", "Kaggle 437 destinasi · kurasi 6 (Perda, OSM)\nrekap anonim kuesioner bobot")
box(ax, 0.2, 1.75, 4.3, 1.25, "Preprocessing bersama", "443 ID dipertahankan · fitur C1–C6\nmanifest hash + fingerprint")
box(ax, 0.2, 0.2, 4.3, 1.25, "Artefak", "CSV destinasi · CSV fitur K-Means\nJSON model K-Means (centroid, label)")
arrow(ax, (2.35, 3.28), (2.35, 3.02)); arrow(ax, (2.35, 1.73), (2.35, 1.47))
box(ax, 5.1, 3.3, 3.9, 1.25, "Formulir preferensi", "budget tiket · kota asal · provinsi\nkategori · hobi · profil bobot")
box(ax, 5.1, 1.75, 3.9, 1.25, "Mesin SPK", "filter provinsi + tiket ≤ budget\nmatriks C1–C6 · AHP · TOPSIS")
box(ax, 5.1, 0.2, 3.9, 1.25, "Hasil", "Top 10 + skor V · alasan per kriteria\nlabel segmen · peta provinsi")
arrow(ax, (7.05, 3.28), (7.05, 3.02)); arrow(ax, (7.05, 1.73), (7.05, 1.47))
arrow(ax, (4.52, 0.82), (5.08, 2.2))
fig.savefig(f"{OUT}/gambar2_arsitektur.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# Gambar 4: bobot AHP profil Seimbang (kuesioner) vs bobot lama
crit = ["C1 Harga\ntiket", "C2 Rating", "C3 Jarak", "C4 Fasilitas", "C5 Kategori", "C6 Hobi"]
new = [16.13, 13.51, 7.90, 13.23, 26.04, 23.19]; old = [26.93, 17.85, 15.67, 8.20, 15.67, 15.67]
fig, ax = plt.subplots(figsize=(8.0, 3.6))
xs = range(len(crit)); bw = 0.38
b1 = ax.bar([x - bw / 2 for x in xs], old, bw, color="#b9cdc7", label="Rancangan awal pengembang (CR 0,008)")
b2 = ax.bar([x + bw / 2 for x in xs], new, bw, color=TEAL, label="Kuesioner 28 responden (CR 0,060)")
for bars in (b1, b2):
    for r in bars: ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.5, f"{r.get_height():.1f}".replace(".", ","), ha="center", fontsize=8.5)
ax.set_xticks(list(xs)); ax.set_xticklabels(crit, fontsize=10); ax.set_ylabel("Bobot (%)", fontsize=10)
ax.set_ylim(0, 30); ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, fontsize=9, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
fig.savefig(f"{OUT}/gambar4_bobot.png", dpi=220, bbox_inches="tight"); plt.close(fig)
print("ok")
