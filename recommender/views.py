"""View rekomendasi: form preferensi + ranking TOPSIS."""

from django.db.models import Count
from django.shortcuts import render

from recommender.forms import KOTA_ASAL, PreferensiForm
from recommender.models import Destination
from recommender.spk import geo, profiles, similarity, topsis

NAMA_KRITERIA = ["Harga tiket", "Rating", "Jarak", "Fasilitas", "Kategori", "Hobi"]
TOP_N = 10


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


def rekomendasi(request):
    if request.method == "POST":
        form = PreferensiForm(request.POST)
    else:
        form = PreferensiForm(initial={"wilayah": request.GET.get("wilayah", "")})
    konteks = {"form": form, "hasil": None, "kandidat_kosong": False,
               "bobot_efektif": None, "mode_custom": False, "pesan": ""}
    if request.method != "POST" or not form.is_valid():
        return render(request, "recommender/form_hasil.html", konteks)

    cd = form.cleaned_data
    bobot = list(profiles.ACTIVE_PROFILES[cd["profil"]]["weights"])
    mode_custom = False
    slider_keys = ("w1", "w2", "w3", "w4", "w5", "w6")
    slider_disentuh = any(k in form.data for k in slider_keys)
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
        return render(request, "recommender/form_hasil.html", konteks)

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

    hasil, untuk_sesi = [], []
    for r in ranking:
        d = kandidat[r["idx"]]
        hasil.append({"nama": d.nama, "kategori": d.kategori, "harga": d.harga_tiket,
                      "rating": d.rating, "vi": r["vi"],
                      "cluster": d.cluster_label or "-",
                      "alasan": _bangun_alasan(r["gap"])})
        untuk_sesi.append({"nama": d.nama, "provinsi": d.provinsi, "vi": r["vi"],
                           "latitude": d.latitude, "longitude": d.longitude})
    request.session["hasil_terakhir"] = untuk_sesi
    konteks.update({"hasil": hasil, "bobot_efektif": bobot, "mode_custom": mode_custom})
    return render(request, "recommender/form_hasil.html", konteks)


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
