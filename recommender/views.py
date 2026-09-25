"""View rekomendasi: form preferensi + ranking TOPSIS."""

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
    konteks.update({"hasil": hasil, "bobot_efektif": bobot})
    return render(request, "recommender/form_hasil.html", konteks)
