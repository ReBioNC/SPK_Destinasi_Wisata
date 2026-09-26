"""Form preferensi pengguna (Bahasa Indonesia)."""

from django import forms

from recommender.kota_asal import KOTA_ASAL
from recommender.models import Destination
from recommender.spk import profiles


def parse_budget(value):
    """Terima '250000', '250.000', '250,000', 'Rp 250000' -> int.

    Tanda minus di depan ditolak (budget negatif tidak masuk akal).
    """
    teks = str(value).strip()
    if teks.startswith("-"):
        raise forms.ValidationError("Masukkan budget dalam angka, contoh: 250000.")
    digits = "".join(ch for ch in teks if ch.isdigit())
    if not digits:
        raise forms.ValidationError("Masukkan budget dalam angka, contoh: 250000.")
    return int(digits)


class PreferensiForm(forms.Form):
    budget = forms.CharField(label="Budget maksimal (Rp)", max_length=20,
        help_text="Contoh: 250000. Destinasi dengan harga tiket di atas budget otomatis tersaring.")
    kota_asal = forms.ChoiceField(label="Kota asal", choices=[],
        help_text="Titik berangkat Anda; menentukan jarak tempuh (C3) ke setiap destinasi.")
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kota_asal"].choices = [(k, k) for k in KOTA_ASAL]
        wilayah = sorted(Destination.objects.values_list("provinsi", flat=True).distinct())
        self.fields["wilayah"].choices = [(w, w) for w in wilayah]
        kategori = sorted(Destination.objects.values_list("kategori", flat=True).distinct())
        self.fields["kategori_utama"].choices = [(k, k) for k in kategori]
        self.fields["kategori_sekunder"].choices = [(k, k) for k in kategori]
        tags = set()
        for raw in Destination.objects.values_list("tag_aktivitas", flat=True):
            tags.update(t for t in (raw or "").split("|") if t)
        self.fields["hobi"].choices = [(t, t) for t in sorted(tags)]
        self.fields["profil"].choices = [(k, v["label"]) for k, v in profiles.ACTIVE_PROFILES.items()]

    def clean_budget(self):
        return parse_budget(self.cleaned_data["budget"])
