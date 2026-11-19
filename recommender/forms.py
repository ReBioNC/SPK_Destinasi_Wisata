"""Form preferensi pengguna (Bahasa Indonesia)."""

from django import forms
import re

from recommender.kota_asal import KOTA_ASAL
from recommender.models import Destination
from recommender.spk import profiles


# Batas atas budget tiket per orang. Jauh di atas tiket termahal di dataset (Rp 900.000),
# jadi tidak menyaring destinasi; hanya mencegah angka ekstrem.
MAX_BUDGET = 1_000_000_000


def parse_budget(value):
    """Terima '250000', '250.000', '250,000', 'Rp 250000' -> int.

    Tanda minus di depan ditolak (budget negatif tidak masuk akal). Budget di atas
    MAX_BUDGET ditolak dengan pesan yang menyebut batasnya.
    """
    teks = str(value).strip()
    if not re.fullmatch(r"(?:Rp\s*)?(?:\d+|\d{1,3}(?:[.,]\d{3})+)", teks, re.IGNORECASE):
        raise forms.ValidationError("Masukkan budget dalam angka, contoh: 250000.")
    budget = int(re.sub(r"[.,]", "", re.sub(r"^Rp\s*", "", teks, flags=re.IGNORECASE)))
    if budget > MAX_BUDGET:
        raise forms.ValidationError("Budget maksimal Rp 1.000.000.000 per orang.")
    return budget


class PreferensiForm(forms.Form):
    # Tanpa max_length: format ribuan dari JS menambah karakter, batas dicek secara numerik di parse_budget.
    budget = forms.CharField(label="Budget maksimal tiket masuk (Rp/orang)",
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
        help_text="Contoh: 500000. Batas harga tiket satu destinasi per orang, maksimal Rp 1.000.000.000. Nilai 0 tetap menerima destinasi gratis.")
    kota_asal = forms.ChoiceField(label="Kota asal", choices=[],
        help_text="Titik berangkat Anda; menentukan jarak garis lurus (C3) ke setiap destinasi.")
    wilayah = forms.ChoiceField(label="Wilayah tujuan (provinsi)", choices=[],
        help_text="Hanya destinasi di provinsi ini yang dinilai. Bisa juga dipilih lewat halaman Peta.")
    kategori_utama = forms.ChoiceField(label="Kategori utama", choices=[],
        help_text="Minat utama Anda; destinasi kategori ini mendapat skor penuh (1).")
    kategori_sekunder = forms.ChoiceField(label="Kategori sekunder", choices=[],
        help_text="Minat kedua; mendapat skor setengah (0,5). Kategori lain bernilai 0, bukan tersaring.")
    hobi = forms.MultipleChoiceField(label="Hobi", choices=[], required=False,
                                     widget=forms.CheckboxSelectMultiple,
        help_text="Dicocokkan dengan aktivitas destinasi (mis. hiking, fotografi). Boleh dikosongkan.")
    profil = forms.ChoiceField(label="Profil prioritas", choices=[], widget=forms.RadioSelect,
        help_text="Menentukan seberapa besar pengaruh tiap kriteria. Penjelasan tiap profil ada di bawah.")
    sentuh_bobot = forms.CharField(required=False, widget=forms.HiddenInput)
    w1 = forms.FloatField(required=False, min_value=0, max_value=100)
    w2 = forms.FloatField(required=False, min_value=0, max_value=100)
    w3 = forms.FloatField(required=False, min_value=0, max_value=100)
    w4 = forms.FloatField(required=False, min_value=0, max_value=100)
    w5 = forms.FloatField(required=False, min_value=0, max_value=100)
    w6 = forms.FloatField(required=False, min_value=0, max_value=100)

    def __init__(self, *args, options=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kota_asal"].choices = [(k, k) for k in KOTA_ASAL]
        if options is None:
            rows = Destination.objects.values_list("provinsi", "kategori", "tag_aktivitas")
            wilayah = sorted({row[0] for row in rows})
            kategori = sorted({row[1] for row in rows})
            tags = sorted({t for row in rows for t in (row[2] or "").split("|") if t})
        else:
            wilayah, kategori, tags = options
        self.fields["wilayah"].choices = [(w, w) for w in wilayah]
        self.fields["kategori_utama"].choices = [(k, k) for k in kategori]
        self.fields["kategori_sekunder"].choices = [(k, k) for k in kategori]
        # Value tetap tag asli; label hanya dirapikan untuk tampilan (rekreasi_keluarga -> rekreasi keluarga).
        self.fields["hobi"].choices = [(t, t.replace("_", " ")) for t in tags]
        self.fields["profil"].choices = [(k, v["label"]) for k, v in profiles.ACTIVE_PROFILES.items()]

    def clean_budget(self):
        return parse_budget(self.cleaned_data["budget"])
