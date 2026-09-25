"""Form preferensi pengguna (Bahasa Indonesia)."""

from django import forms

from recommender.models import Destination
from recommender.spk import profiles

KOTA_ASAL = {
    "Jakarta": (-6.2088, 106.8456),
    "Bandung": (-6.9175, 107.6191),
    "Semarang": (-6.9667, 110.4167),
    "Surabaya": (-7.2575, 112.7521),
    "Yogyakarta": (-7.7956, 110.3695),
    "Medan": (3.5952, 98.6722),
    "Makassar": (-5.1477, 119.4327),
    "Denpasar": (-8.6705, 115.2126),
}


def parse_budget(value):
    """Terima '250000', '250.000', '250,000', 'Rp 250000' -> int."""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        raise forms.ValidationError("Masukkan budget dalam angka, contoh: 250000.")
    return int(digits)


class PreferensiForm(forms.Form):
    budget = forms.CharField(label="Budget maksimal (Rp)", max_length=20)
    kota_asal = forms.ChoiceField(label="Kota asal", choices=[])
    wilayah = forms.ChoiceField(label="Wilayah tujuan (provinsi)", choices=[])
    kategori_utama = forms.ChoiceField(label="Kategori utama", choices=[])
    kategori_sekunder = forms.ChoiceField(label="Kategori sekunder", choices=[])
    hobi = forms.MultipleChoiceField(label="Hobi", choices=[], required=False,
                                     widget=forms.CheckboxSelectMultiple)
    profil = forms.ChoiceField(label="Profil prioritas", choices=[], widget=forms.RadioSelect)

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
