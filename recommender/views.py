"""View rekomendasi: form preferensi + ranking TOPSIS."""

from django.db.models import Count
from django.shortcuts import render

from recommender.forms import KOTA_ASAL, PreferensiForm
from recommender.models import Destination
from recommender.spk import geo, profiles, similarity, topsis

NAMA_KRITERIA = ["Harga tiket", "Rating", "Jarak", "Fasilitas", "Kategori", "Hobi"]
TOP_N = 10

FAS_LABEL = [("fas_toilet", "Toilet"), ("fas_parkir", "Parkir"), ("fas_warung", "Warung"),
             ("fas_mushola", "Mushola"), ("fas_penginapan", "Penginapan")]


def _rupiah(nilai):
    """Format 'Rp 150.000'."""
    return "Rp " + f"{int(nilai):,}".replace(",", ".")


def _daftar_pilihan():
    """Opsi select untuk template: wilayah, kategori, hobi (urut abjad)."""
    wilayah = sorted(Destination.objects.values_list("provinsi", flat=True).distinct())
    kategori = sorted(Destination.objects.values_list("kategori", flat=True).distinct())
    tags = set()
    for raw in Destination.objects.values_list("tag_aktivitas", flat=True):
        tags.update(t for t in (raw or "").split("|") if t)
    return wilayah, kategori, sorted(tags)


def _kartu_profil():
    """Profil + persen dominan + bobot persen untuk slider/data-w."""
    info = []
    for key, p in profiles.ACTIVE_PROFILES.items():
        j = max(range(len(p["weights"])), key=lambda i: p["weights"][i])
        info.append({"key": key, "label": p["label"],
                     "dominan": NAMA_KRITERIA[j],
                     "persen": round(p["weights"][j] * 100),
                     "blurb": PROFIL_BLURB[key],
                     "w_pct": [round(w * 100) for w in p["weights"]]})
    return info


def _seleksi_saat_ini(request, form):
    """Nilai terpilih untuk render ulang form (POST diutamakan)."""
    if request.method == "POST":
        hobi = list(request.POST.getlist("hobi"))
        get = lambda k, d="": request.POST.get(k, d)
    else:
        hobi = []
        get = lambda k, d="": form.initial.get(k, d)
    return {"budget": get("budget", ""), "kota": get("kota_asal", ""),
            "wilayah": get("wilayah", ""), "kutama": get("kategori_utama", ""),
            "ksekunder": get("kategori_sekunder", ""),
            "hobi": hobi, "profil": get("profil", "") or "seimbang"}


def _bangun_alasan(gap):
    """Kalimat explainability dari gap ke solusi ideal (kecil = baik)."""
    urut = sorted(range(len(gap)), key=lambda j: gap[j])
    unggul = ", ".join(NAMA_KRITERIA[j] for j in urut[:2])
    tertahan = NAMA_KRITERIA[urut[-1]]
    return f"Unggul pada {unggul}; tertahan oleh {tertahan}."


def _skor_c5(kategori, utama, sekunder):
    if kategori == utama:
        return 1.0
    if kategori == sekunder:
        return 0.5
    return 0.0


def normalisasi_bobot(vektor):
    """Normalisasi vektor bobot agar berjumlah 1."""
    total = sum(vektor)
    return [v / total for v in vektor]


PROFIL_BLURB = {
    "hemat": "Pilih ini bila budget adalah prioritas utama liburan Anda.",
    "kualitas": "Pilih ini bila pengalaman terbaik yang utama, soal harga nomor dua.",
    "petualang": "Pilih ini bila ingin destinasi yang mudah dijangkau dan sesuai hobi.",
    "seimbang": "Pilihan aman untuk umum; semua kriteria dipertimbangkan proporsional.",
}


def info_profil():
    """Deskripsi tiap profil: kriteria dominan + persen bobot aktual."""
    info = []
    for key, p in profiles.ACTIVE_PROFILES.items():
        j = max(range(len(p["weights"])), key=lambda i: p["weights"][i])
        info.append({"key": key, "label": p["label"],
                     "dominan": NAMA_KRITERIA[j],
                     "persen": round(p["weights"][j] * 100),
                     "blurb": PROFIL_BLURB[key]})
    return info


def rekomendasi(request):
    wilayah_valid = set(Destination.objects.values_list("provinsi", flat=True).distinct())
    if request.method == "POST":
        form = PreferensiForm(request.POST)
    else:
        param = request.GET.get("wilayah", "")
        form = PreferensiForm(initial={"wilayah": param} if param in wilayah_valid else None)
    konteks = {"form": form, "hasil": None, "kandidat_kosong": False,
               "bobot_efektif": None, "mode_custom": False, "pesan": "",
               "pesan_class": "warning", "profil_info": info_profil(),
               "kota_list": list(KOTA_ASAL.keys()),
               "wilayah_list": sorted(Destination.objects.values_list("provinsi", flat=True).distinct()),
               "kategori_list": sorted(Destination.objects.values_list("kategori", flat=True).distinct()),
               "hobi_list": sorted({t for raw in Destination.objects.values_list("tag_aktivitas", flat=True)
                                    for t in (raw or "").split("|") if t}),
               "profil_cards": _kartu_profil(),
               "bobot_persen": [round(w * 100) for w in
                                profiles.ACTIVE_PROFILES["seimbang"]["weights"]],
               "cluster_list": [], "ringkasan": None,
               "cur": _seleksi_saat_ini(request, form)}
    if request.method == "GET" and request.GET.get("wilayah", "") in wilayah_valid:
        konteks["pesan"] = (f"Wilayah tujuan terisi dari peta: {request.GET['wilayah']} — "
                            "lengkapi preferensi lain lalu klik Cari Rekomendasi.")
        konteks["pesan_class"] = "success"
    if request.method != "POST" or not form.is_valid():
        return render(request, "recommender/beranda.html", konteks)

    cd = form.cleaned_data
    bobot = list(profiles.ACTIVE_PROFILES[cd["profil"]]["weights"])
    mode_custom = False
    # Slider selalu terkirim browser; hanya jadi sinyal bila user
    # benar-benar menggesernya (hidden sentuh_bobot = "1" via onchange).
    slider_disentuh = cd.get("sentuh_bobot") == "1"
    slider = [(cd.get(f"w{i}") or 0) for i in range(1, 7)]
    if slider_disentuh:
        if sum(slider) > 0:
            bobot = normalisasi_bobot(slider)
            mode_custom = True
        else:
            konteks["pesan"] = ("Bobot kustom nol semua, dipakai bobot profil "
                                f"{profiles.ACTIVE_PROFILES[cd['profil']]['label']}.")
    olat, olon = KOTA_ASAL[cd["kota_asal"]]
    hobi_user = set(cd["hobi"])

    kandidat = list(Destination.objects.filter(
        provinsi=cd["wilayah"], harga_tiket__lte=cd["budget"],
        latitude__isnull=False, longitude__isnull=False))
    if not kandidat:
        konteks["kandidat_kosong"] = True
        konteks["pesan"] = ("Tidak ada destinasi yang cocok. Coba longgarkan budget "
                            "atau pilih wilayah lain.")
        return render(request, "recommender/beranda.html", konteks)

    matriks = []
    for d in kandidat:
        matriks.append([
            float(d.harga_tiket),
            float(d.rating),
            geo.haversine(olat, olon, d.latitude, d.longitude),
            d.facility_score(),
            _skor_c5(d.kategori, cd["kategori_utama"], cd["kategori_sekunder"]),
            similarity.jaccard(hobi_user, d.tag_set()),
        ])
    ranking = topsis.rank(matriks, bobot, profiles.IS_COST)[:TOP_N]

    # Normalisasi gap ke solusi ideal per kriteria (0-100, besar = dekat ideal).
    kolom_gap = list(zip(*[r["gap"] for r in ranking]))

    def _pct_gap(g, kolom):
        mn, mx = min(kolom), max(kolom)
        if mx <= mn:
            return 100
        return round(100 * (1 - (g - mn) / (mx - mn)))

    hasil, untuk_sesi = [], []
    for r in ranking:
        d = kandidat[r["idx"]]
        baris = matriks[r["idx"]]
        skor_c5 = baris[4]
        c5_txt = (f"Utama: {d.kategori}" if skor_c5 >= 1.0
                  else f"Kedua: {d.kategori}" if skor_c5 > 0 else "Beda minat")
        fas_nama = [label for f, label in FAS_LABEL if getattr(d, f)]
        vi = r["vi"]
        hasil.append({"nama": d.nama, "kategori": d.kategori, "harga": d.harga_tiket,
                      "harga_fmt": _rupiah(d.harga_tiket),
                      "rating": d.rating, "vi": vi,
                      "vi_pct": round(vi * 100, 2),
                      "jarak_km": round(baris[2], 1),
                      "jarak_txt": f"± {baris[2]:.0f} km dari {cd['kota_asal']}",
                      "cluster": d.cluster_label or "-",
                      "alasan": _bangun_alasan(r["gap"]),
                      "bars": [
                          {"nama": "C1 Harga", "pct": _pct_gap(r["gap"][0], kolom_gap[0]),
                           "sub": _rupiah(baris[0])},
                          {"nama": "C2 Rating", "pct": _pct_gap(r["gap"][1], kolom_gap[1]),
                           "sub": f"★ {baris[1]:g} / 5.0"},
                          {"nama": "C3 Jarak", "pct": _pct_gap(r["gap"][2], kolom_gap[2]),
                           "sub": f"± {baris[2]:.0f} km"},
                          {"nama": "C4 Fasilitas", "pct": _pct_gap(r["gap"][3], kolom_gap[3]),
                           "sub": ", ".join(fas_nama) or "-"},
                          {"nama": "C5 Kategori", "pct": _pct_gap(r["gap"][4], kolom_gap[4]),
                           "sub": c5_txt},
                          {"nama": "C6 Hobi", "pct": _pct_gap(r["gap"][5], kolom_gap[5]),
                           "sub": f"Jaccard {round(baris[5] * 100)}%"},
                      ]})
        untuk_sesi.append({"nama": d.nama, "provinsi": d.provinsi, "vi": r["vi"],
                           "latitude": d.latitude, "longitude": d.longitude})
    request.session["hasil_terakhir"] = untuk_sesi
    konteks.update({"hasil": hasil, "bobot_efektif": bobot, "mode_custom": mode_custom,
                    "bobot_persen": [round(w * 100) for w in bobot],
                    "cluster_list": sorted({h["cluster"] for h in hasil}),
                    "ringkasan": {"wilayah": cd["wilayah"],
                                  "budget_fmt": _rupiah(cd["budget"]),
                                  "profil": profiles.ACTIVE_PROFILES[cd["profil"]]["label"],
                                  "n": len(kandidat)}})
    return render(request, "recommender/beranda.html", konteks)


def peta(request):
    """Peta interaktif + daftar hasil terakhir (fallback: agregat provinsi)."""
    hasil = request.session.get("hasil_terakhir") or []
    agregat = (Destination.objects.values("provinsi")
               .annotate(jumlah=Count("id")).order_by("provinsi"))
    return render(request, "recommender/peta.html",
                  {"hasil_json": hasil, "agregat": list(agregat),
                   "ada_hasil": bool(hasil)})


def tentang(request):
    """Metodologi singkat + tautan file bukti."""
    return render(request, "recommender/tentang.html")
