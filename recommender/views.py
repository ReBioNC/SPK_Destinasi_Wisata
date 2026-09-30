"""View rekomendasi: form preferensi + ranking TOPSIS."""

import math
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from recommender.forms import KOTA_ASAL, PreferensiForm
from recommender.jarak import jarak_table
from recommender.kota_asal import PROVINSI_KOTA
from recommender.models import Destination
from recommender.spk import geo, profiles, similarity, topsis
from recommender.spk.biaya import MODA, PELABUHAN, estimasi_total
from recommender.transport import MODE_ANTAR, koridor_ports, rencanakan

NAMA_KRITERIA = ["Estimasi biaya total", "Rating", "Jarak", "Fasilitas", "Kategori", "Hobi"]
TOP_N = 10

FAS_LABEL = [("fas_toilet", "Toilet"), ("fas_parkir", "Parkir"), ("fas_warung", "Warung"),
             ("fas_mushola", "Tempat ibadah"), ("fas_accessibility", "Aksesibilitas"),
             ("fas_information_center", "Pusat informasi")]

JAVA_PROVINCES = ('Banten', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah',
                  'Daerah Istimewa Yogyakarta', 'Jawa Timur')


def _map_context(request):
    """Retain every destination; the legacy SVG has schematic, not GIS, precision.

    Affine display coordinates are anchored to Monas within the existing Jakarta
    outline. They do NOT overwrite geographic coordinates or validate boundaries.
    """
    counts = dict(Destination.objects.values_list('provinsi').annotate(n=Count('id')))
    destinations = []
    for d in Destination.objects.order_by('source_id', 'id'):
        valid = (d.latitude is not None and d.longitude is not None
                 and math.isfinite(d.latitude) and math.isfinite(d.longitude))
        x = 260 + (d.longitude - 106.827153) * 21.3 if valid else None
        y = 309 + (-d.latitude - 6.175392) * 24.3 if valid else None
        outside = not valid or not (220 <= x <= 462 and 287 <= y <= 384)
        destinations.append({'source_id': d.source_id or d.id, 'nama': d.nama,
                             'provinsi': d.provinsi, 'kategori': d.kategori,
                             'latitude': d.latitude, 'longitude': d.longitude,
                             'x': round(x, 3) if valid else None, 'y': round(y, 3) if valid else None,
                             'outside_frame': outside, 'quality_notes': _quality_notes(d),
                             'cluster': d.cluster_label or 'Belum dikelompokkan',
                             'source_label': 'Kurasi Jawa' if d.sumber_data == 'curated_java' else 'Kaggle',
                             'curated': d.sumber_data == 'curated_java'})
    return {'map_provinces': [{'nama': p, 'count': counts.get(p, 0)} for p in JAVA_PROVINCES],
            'map_destinations': destinations,
            'hasil_json': request.session.get('hasil_terakhir') or []}


def _dataset_state():
    groups = list(Destination.objects.values("sumber_data", "pipeline_fingerprint").annotate(n=Count("id")))
    counts = {}
    for group in groups:
        counts[group["sumber_data"]] = counts.get(group["sumber_data"], 0) + group["n"]
    fingerprint = "|".join(sorted({group["pipeline_fingerprint"] for group in groups})) or "unversioned"
    return {"data_count": sum(counts.values()), "source_counts": counts,
            "dataset_fingerprint": fingerprint,
            "province_count": Destination.objects.values("provinsi").distinct().count()}


def _sync_session(request, state):
    if request.session.get("dataset_fingerprint") != state["dataset_fingerprint"]:
        request.session.pop("flash_hasil", None)
        request.session.pop("hasil_terakhir", None)
    request.session["dataset_fingerprint"] = state["dataset_fingerprint"]


def _quality_notes(destination):
    notes = []
    if destination.rating_imputed:
        notes.append(destination.data_quality.get("rating_model_note") or "Rating diimputasi median; bukan rating teramati.")
    if destination.data_quality.get("coordinate_review_required"):
        notes.append(destination.data_quality.get("coordinate_review_note") or "Koordinat perlu review.")
    if destination.data_quality.get("facility_review_note"):
        notes.append(destination.data_quality["facility_review_note"])
    return notes


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
        hobi = list(form.initial.get('hobi', []))
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
    state = _dataset_state()
    _sync_session(request, state)
    wilayah_list, kategori_list, hobi_list = _daftar_pilihan()
    options = (wilayah_list, kategori_list, hobi_list)
    wilayah_valid = set(wilayah_list)
    if request.method == "POST":
        form = PreferensiForm(request.POST, options=options)
    else:
        param = request.GET.get("wilayah", "")
        initial = dict(request.session.get('preference_input') or {})
        if param in wilayah_valid:
            initial['wilayah'] = param
        form = PreferensiForm(initial=initial, options=options)
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
               "cur": _seleksi_saat_ini(request, form), **state, **_map_context(request)}
    form.fields['kota_asal'].choices = konteks['kota_list']
    selected_profile = profiles.ACTIVE_PROFILES.get(konteks['cur']['profil'], profiles.ACTIVE_PROFILES['seimbang'])
    defaults = [round(w * 100) for w in selected_profile['weights']]
    konteks['custom_selected'] = form['sentuh_bobot'].value() == '1'
    konteks['slider_fields'] = [
        {'name': f'w{i+1}', 'label': label,
         'value': form[f'w{i+1}'].value() if form[f'w{i+1}'].value() not in (None, '') else defaults[i]}
        for i, label in enumerate(NAMA_KRITERIA)]
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
            return JsonResponse({"ok": False, "errors": dict(form.errors),
                                 "labels": {name: form.fields[name].label for name in form.errors},
                                 "pesan": "Preferensi belum lengkap atau tidak valid."},
                                status=400)
        return render(request, "recommender/beranda.html", konteks)

    cd = form.cleaned_data
    # Retain only declared preference fields, never CSRF or arbitrary POST keys.
    request.session['preference_input'] = {
        name: request.POST.getlist(name) if name == 'hobi' else request.POST.get(name, '')
        for name in form.fields}
    request.session.pop('flash_hasil', None)
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
        request.session['hasil_terakhir'] = []
        if _is_ajax(request):
            return _ajax_results(request, konteks, 0)
        request.session["flash_hasil"] = {
            "kandidat_kosong": True, "pesan": konteks["pesan"],
            "pesan_class": konteks["pesan_class"]}
        return redirect("beranda")

    # Saring kasar tanpa network: estimasi darat-bawah (haversine) selalu
    # <= total sebenarnya (jarak jalan >= lurus; pesawat/feri >= darat-bawah),
    # sehingga yang gugur di sini pasti gugur juga — aman, tanpa OSRM.
    from recommender.spk.biaya import INAP_PER_MALAM, MAKAN_PER_HARI
    tarif_km = MODA[moda]["tarif_per_km"]
    parkir = MODA[moda]["parkir"]
    makan = hari * MAKAN_PER_HARI
    inap = max(hari - 1, 0) * INAP_PER_MALAM
    lolos_kasar = []
    for d in pra:
        gc = geo.haversine(olat, olon, d.latitude, d.longitude)
        kasar = d.harga_tiket + (2 * gc * tarif_km + parkir) + makan + inap
        if kasar <= cd["budget"]:
            lolos_kasar.append(d)
    # Pra-hangatkan cache jarak sekaligus (Table API): 1-2 request untuk
    # semua kandidat, bukan ratusan request ber-throttle.
    if lolos_kasar:
        jarak_table(olat, olon, [(d.latitude, d.longitude) for d in lolos_kasar],
                    moda)
        koridor = koridor_ports(prov_asal, cd["wilayah"])
        if koridor is not None and mode_antar in ("termurah", "darat_feri"):
            _, pa, pt = koridor
            jarak_table(olat, olon, [PELABUHAN[pa]], moda)
            jarak_table(*PELABUHAN[pt],
                        [(d.latitude, d.longitude) for d in lolos_kasar], moda)
    # Biaya total per kandidat, lalu saring budget atas TOTAL (bukan tiket).
    terpilih = []
    for d in lolos_kasar:
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
        request.session['hasil_terakhir'] = []
        if _is_ajax(request):
            return _ajax_results(request, konteks, 0)
        request.session["flash_hasil"] = {
            "kandidat_kosong": True, "pesan": konteks["pesan"],
            "pesan_class": konteks["pesan_class"]}
        return redirect("beranda")

    matriks = []
    for d, plan, rinc in terpilih:
        matriks.append([
            float(rinc["total"]),
            d.calculation_rating(),
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
                      "source_id": d.source_id, "rating_model": d.calculation_rating(),
                      "rating_imputed": d.rating_imputed, "provenance": d.provenance,
                      "quality_notes": _quality_notes(d), "facility_score": d.facility_score(),
                      "source_label": ("Kaggle" if d.sumber_data == "kaggle_java" else
                                       "Kurasi Jawa" if d.sumber_data == "curated_java" else "Sumber lama/belum dimigrasi"),
                      "harga_fmt": _rupiah(total),
                      "rating": d.rating, "vi": vi,
                      "vi_pct": round(vi * 100, 2),
                      "jarak_km": round(baris[2], 1),
                      "jarak_txt": f"± {baris[2]:.0f} km ({plan['cara']}) dari {cd['kota_asal']}",
                      "rincian": rincian, "rincian_txt": rincian_txt,
                      "cluster": d.cluster_label or "Belum dikelompokkan",
                      "simulasi": False,
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
                           "source_id": d.source_id, "quality_notes": _quality_notes(d),
                           "latitude": d.latitude, "longitude": d.longitude,
                           "total": total})
    request.session["hasil_terakhir"] = untuk_sesi
    ringkasan = {"wilayah": cd["wilayah"], "budget_fmt": _rupiah(cd["budget"]),
                 "profil": profiles.ACTIVE_PROFILES[cd["profil"]]["label"],
                 "n": len(kandidat),
                 "moda": MODA[moda]["label"], "hari": hari,
                 "mode_antar": dict(MODE_ANTAR)[mode_antar],
                 "n_simulasi": 0}
    konteks.update({"hasil": hasil, "bobot_efektif": bobot, "mode_custom": mode_custom,
                    "bobot_persen": [round(w * 100) for w in bobot],
                    "cluster_list": sorted({h["cluster"] for h in hasil}),
                    "ringkasan": ringkasan})
    if _is_ajax(request):
        return _ajax_results(request, konteks, len(hasil))
    # POST-Redirect-GET: hasil tampil sekali, refresh berikutnya bersih.
    request.session["flash_hasil"] = {
        "hasil": hasil, "mode_custom": mode_custom,
        "pesan": konteks["pesan"], "pesan_class": konteks["pesan_class"],
        "bobot_persen": [round(w * 100) for w in bobot],
        "cluster_list": sorted({h["cluster"] for h in hasil}),
        "ringkasan": ringkasan}
    return redirect("beranda")


def _ajax_results(request, context, count):
    """Cards and the inline map's latest-results list share one response snapshot."""
    map_context = {'hasil_json': request.session.get('hasil_terakhir') or []}
    return JsonResponse({'ok': True, 'count': count,
                         'html': render_to_string('recommender/_hasil.html', context, request),
                         'map_html': render_to_string('recommender/_map_results.html', map_context, request)})


def _is_ajax(request):
    """True bila request fetch AJAX (header X-Requested-With)."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def peta(request):
    """Peta interaktif + daftar hasil terakhir (fallback: agregat provinsi)."""
    state = _dataset_state()
    _sync_session(request, state)
    return render(request, "recommender/peta.html", {**state, **_map_context(request)})


def tentang(request):
    """Metodologi singkat + tautan file bukti."""
    return render(request, "recommender/tentang.html", _dataset_state())
