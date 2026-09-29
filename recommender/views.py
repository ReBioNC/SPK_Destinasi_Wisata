"""View rekomendasi: form preferensi + ranking TOPSIS."""

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from recommender.forms import KOTA_ASAL, PreferensiForm
from recommender.kota_asal import PROVINSI_KOTA
from recommender.models import Destination
from recommender.spk import geo, profiles, similarity, topsis
from recommender.spk.biaya import MODA, estimasi_total
from recommender.transport import MODE_ANTAR, rencanakan

NAMA_KRITERIA = ["Harga tiket", "Rating", "Jarak", "Fasilitas", "Kategori", "Hobi"]
TOP_N = 10

FAS_LABEL = [("fas_toilet", "Toilet"), ("fas_parkir", "Parkir"), ("fas_warung", "Warung"),
             ("fas_mushola", "Mushola")]


def _rupiah(nilai):
    """Format 'Rp 150.000'."""
    return "Rp " + f"{int(nilai):,}".replace(",", ".")


def _daftar_pilihan():
    """Opsi form dan template dari satu pembacaan data destinasi."""
    rows = Destination.objects.values_list("provinsi", "kategori", "tag_aktivitas")
    wilayah, kategori, tags = set(), set(), set()
    for prov, kat, raw in rows.iterator():
        wilayah.add(prov)
        kategori.add(kat)
        tags.update(t for t in (raw or "").split("|") if t)
    return sorted(wilayah), sorted(kategori), sorted(tags)


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
            "hobi": hobi, "profil": get("profil", "") or "seimbang",
            "moda": get("moda", "") or "mobil",
            "hari": get("hari", "") or "1",
            "mode_antar": get("mode_antar", "") or "termurah"}


def _bangun_alasan(gap, span):
    """Bandingkan posisi tiap kriteria terhadap rentang ideal seluruh kandidat."""
    aktif = [j for j, lebar in enumerate(span) if lebar > 1e-12]
    if not aktif:
        return "Semua kandidat bernilai sama pada kriteria yang digunakan."
    urut = sorted(aktif, key=lambda j: gap[j] / span[j])
    unggul = ", ".join(NAMA_KRITERIA[j] for j in urut[:2])
    tertahan = NAMA_KRITERIA[urut[-1]]
    if len(urut) == 1:
        return f"Paling dekat nilai ideal pada {unggul}."
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
    wilayah_list, kategori_list, hobi_list = _daftar_pilihan()
    options = (wilayah_list, kategori_list, hobi_list)
    wilayah_valid = set(wilayah_list)
    if request.method == "POST":
        form = PreferensiForm(request.POST, options=options)
    else:
        param = request.GET.get("wilayah", "")
        form = PreferensiForm(initial={"wilayah": param} if param in wilayah_valid else None,
                             options=options)
    konteks = {"form": form, "hasil": None, "kandidat_kosong": False,
               "bobot_efektif": None, "mode_custom": False, "pesan": "",
               "pesan_class": "warning", "profil_info": info_profil(),
                "kota_list": [(k, f"{k} ({PROVINSI_KOTA[k]})" if k in PROVINSI_KOTA else k)
                              for k in sorted(KOTA_ASAL)],
               "wilayah_list": wilayah_list,
               "kategori_list": kategori_list,
               "hobi_list": hobi_list,
                "profil_cards": _kartu_profil(),
                "moda_list": [(k, v["label"]) for k, v in MODA.items()],
                "mode_antar_list": list(MODE_ANTAR),
               "bobot_persen": [round(w * 100) for w in
                                profiles.ACTIVE_PROFILES["seimbang"]["weights"]],
               "cluster_list": [], "ringkasan": None,
               "cur": _seleksi_saat_ini(request, form)}
    if request.method == "GET" and request.GET.get("wilayah", "") in wilayah_valid:
        konteks["pesan"] = (f"Wilayah tujuan terisi dari peta: {request.GET['wilayah']} — "
                            "lengkapi preferensi lain lalu klik Cari Rekomendasi.")
        konteks["pesan_class"] = "success"
    if request.method == "GET":
        # Flash sekali tampil: refresh berikutnya bersih seperti sesi baru.
        flash = request.session.pop("flash_hasil", None)
        if flash:
            konteks.update(flash)
    if request.method != "POST" or not form.is_valid():
        if request.method == "POST" and _is_ajax(request):
            return JsonResponse({"ok": False,
                                 "pesan": "Preferensi belum lengkap atau tidak valid."},
                                status=400)
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
    moda, hari, mode_antar = cd["moda"], cd["hari"], cd["mode_antar"]
    try:
        prov_asal = PROVINSI_KOTA[cd["kota_asal"]]
    except KeyError:
        form.add_error("kota_asal", "Kota asal tidak dikenal.")
        return render(request, "recommender/beranda.html", konteks)

    pra = list(Destination.objects.filter(
        provinsi=cd["wilayah"], harga_tiket__lte=cd["budget"],
        latitude__isnull=False, longitude__isnull=False))
    if not pra:
        konteks["kandidat_kosong"] = True
        konteks["pesan"] = ("Tidak ada destinasi yang cocok. Coba longgarkan budget "
                            "atau pilih wilayah lain.")
        if _is_ajax(request):
            return JsonResponse({"ok": True, "count": 0,
                                 "html": render_to_string("recommender/_hasil.html",
                                                          konteks, request)})
        request.session["flash_hasil"] = {
            "kandidat_kosong": True, "pesan": konteks["pesan"],
            "pesan_class": konteks["pesan_class"]}
        return redirect("beranda")

    # Biaya total per kandidat, lalu saring budget atas TOTAL (bukan tiket).
    terpilih = []
    for d in pra:
        plan = rencanakan(olat, olon, prov_asal, d.latitude, d.longitude,
                          d.provinsi, moda, mode_antar)
        rinc = estimasi_total(d.harga_tiket, 0, moda, hari,
                              transport=plan["transport"])
        if rinc["total"] <= cd["budget"]:
            terpilih.append((d, plan, rinc))
    kandidat = [d for d, _, _ in terpilih]
    if not kandidat:
        konteks["kandidat_kosong"] = True
        konteks["pesan"] = ("Tidak ada destinasi yang total biayanya muat di budget. "
                            "Coba naikkan budget, persingkat durasi, atau pilih wilayah lain.")
        if _is_ajax(request):
            return JsonResponse({"ok": True, "count": 0,
                                 "html": render_to_string("recommender/_hasil.html",
                                                          konteks, request)})
        request.session["flash_hasil"] = {
            "kandidat_kosong": True, "pesan": konteks["pesan"],
            "pesan_class": konteks["pesan_class"]}
        return redirect("beranda")

    matriks = []
    for d, plan, rinc in terpilih:
        matriks.append([
            float(rinc["total"]),
            float(d.rating),
            float(plan["jarak_km"]),
            d.facility_score(),
            _skor_c5(d.kategori, cd["kategori_utama"], cd["kategori_sekunder"]),
            similarity.jaccard(hobi_user, d.tag_set()) if hobi_user else 0.0,
        ])
    ranking = topsis.rank(matriks, bobot, profiles.IS_COST)[:TOP_N]
    plans = [p for _, p, _ in terpilih]
    rincs = [c for _, _, c in terpilih]

    def _pct_gap(g, lebar):
        if lebar <= 1e-12:
            return 0
        return max(0, min(100, round(100 * (1 - g / lebar))))

    hasil, untuk_sesi = [], []
    for r in ranking:
        d = kandidat[r["idx"]]
        baris = matriks[r["idx"]]
        plan = plans[r["idx"]]
        rinc = rincs[r["idx"]]
        total = int(rinc["total"])
        rincian = {"tiket": rinc["tiket"], "transport": rinc["transport"],
                   "makan": rinc["makan"], "inap": rinc["inap"], "total": total,
                   "cara": plan["cara"], "sumber_jarak": plan["sumber_jarak"],
                   "plan": plan["rincian"]}
        rincian_txt = (f"Tiket {_rupiah(rinc['tiket'])} + transport "
                       f"{_rupiah(rinc['transport'])} + makan {_rupiah(rinc['makan'])} "
                       f"+ inap {_rupiah(rinc['inap'])} ({plan['cara']}, {plan['sumber_jarak']}).")
        skor_c5 = baris[4]
        c5_txt = (f"Utama: {d.kategori}" if skor_c5 >= 1.0
                  else f"Kedua: {d.kategori}" if skor_c5 > 0 else "Beda minat")
        fas_nama = [label for f, label in FAS_LABEL if getattr(d, f)]
        vi = r["vi"]
        hasil.append({"nama": d.nama, "kategori": d.kategori, "harga": total,
                      "harga_fmt": _rupiah(total),
                      "rating": d.rating, "vi": vi,
                      "vi_pct": round(vi * 100, 2),
                      "jarak_km": round(baris[2], 1),
                      "jarak_txt": f"± {baris[2]:.0f} km ({plan['cara']}) dari {cd['kota_asal']}",
                      "rincian": rincian, "rincian_txt": rincian_txt,
                      "cluster": d.cluster_label or "Belum dikelompokkan",
                      "simulasi": d.sumber_data == "xlsx38",
                      "alasan": (_bangun_alasan(r["gap"], r["span"]) if len(kandidat) > 1
                                 else "Hanya satu destinasi lolos filter; tidak ada pembanding."),
                       "bars": [
                           {"nama": "C1 Total Biaya", "pct": _pct_gap(r["gap"][0], r["span"][0]),
                            "no_effect": r["span"][0] <= 1e-12,
                            "sub": f"Total {_rupiah(total)}"},
                          {"nama": "C2 Rating", "pct": _pct_gap(r["gap"][1], r["span"][1]),
                           "no_effect": r["span"][1] <= 1e-12,
                           "sub": f"★ {baris[1]:g} / 5.0"},
                          {"nama": "C3 Jarak", "pct": _pct_gap(r["gap"][2], r["span"][2]),
                           "no_effect": r["span"][2] <= 1e-12,
                           "sub": f"± {baris[2]:.0f} km"},
                          {"nama": "C4 Fasilitas", "pct": _pct_gap(r["gap"][3], r["span"][3]),
                           "no_effect": r["span"][3] <= 1e-12,
                           "sub": ", ".join(fas_nama) or "-"},
                          {"nama": "C5 Kategori", "pct": _pct_gap(r["gap"][4], r["span"][4]),
                           "no_effect": r["span"][4] <= 1e-12,
                           "sub": c5_txt},
                          {"nama": "C6 Hobi", "pct": _pct_gap(r["gap"][5], r["span"][5]),
                           "no_effect": r["span"][5] <= 1e-12,
                           "sub": f"Jaccard {round(baris[5] * 100)}%" if hobi_user else "Hobi tidak dipilih"},
                      ]})
        untuk_sesi.append({"nama": d.nama, "provinsi": d.provinsi, "vi": r["vi"],
                           "latitude": d.latitude, "longitude": d.longitude,
                           "total": total})
    request.session["hasil_terakhir"] = untuk_sesi
    ringkasan = {"wilayah": cd["wilayah"], "budget_fmt": _rupiah(cd["budget"]),
                 "profil": profiles.ACTIVE_PROFILES[cd["profil"]]["label"],
                 "n": len(kandidat),
                 "moda": MODA[moda]["label"], "hari": hari,
                 "mode_antar": dict(MODE_ANTAR)[mode_antar],
                 "n_simulasi": sum(d.sumber_data == "xlsx38" for d in kandidat)}
    konteks.update({"hasil": hasil, "bobot_efektif": bobot, "mode_custom": mode_custom,
                    "bobot_persen": [round(w * 100) for w in bobot],
                    "cluster_list": sorted({h["cluster"] for h in hasil}),
                    "ringkasan": ringkasan})
    if _is_ajax(request):
        return JsonResponse({"ok": True, "count": len(hasil),
                             "html": render_to_string("recommender/_hasil.html",
                                                      konteks, request)})
    # POST-Redirect-GET: hasil tampil sekali, refresh berikutnya bersih.
    request.session["flash_hasil"] = {
        "hasil": hasil, "mode_custom": mode_custom,
        "pesan": konteks["pesan"], "pesan_class": konteks["pesan_class"],
        "bobot_persen": [round(w * 100) for w in bobot],
        "cluster_list": sorted({h["cluster"] for h in hasil}),
        "ringkasan": ringkasan}
    return redirect("beranda")


def _is_ajax(request):
    """True bila request fetch AJAX (header X-Requested-With)."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


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
