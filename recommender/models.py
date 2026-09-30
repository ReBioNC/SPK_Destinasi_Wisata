from django.db import models
import math


class Destination(models.Model):
    """Satu destinasi wisata. Kunci natural: (nama, kota)."""

    nama = models.CharField(max_length=200)
    kota = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100, db_index=True)
    kategori = models.CharField(max_length=50, db_index=True)
    sub_kategori = models.CharField(max_length=100, blank=True, default="")
    harga_tiket = models.IntegerField(db_index=True)
    source_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    rating_model = models.FloatField(null=True, blank=True)
    rating_imputed = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")
    provenance = models.JSONField(default=dict, blank=True)
    data_quality = models.JSONField(default=dict, blank=True)
    pipeline_fingerprint = models.CharField(max_length=64, blank=True, default="")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    fas_toilet = models.BooleanField(default=False)
    fas_parkir = models.BooleanField(default=False)
    fas_warung = models.BooleanField(default=False)
    fas_mushola = models.BooleanField(default=False)
    fas_accessibility = models.BooleanField(default=False)
    fas_information_center = models.BooleanField(default=False)
    fas_penginapan = models.BooleanField(default=False)
    tag_aktivitas = models.TextField(blank=True, default="")
    cluster_label = models.CharField(max_length=100, blank=True, default="")
    sumber_data = models.CharField(max_length=20, default="xlsx38")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["nama", "kota"], name="uniq_nama_kota"),
        ]

    def __str__(self):
        return f"{self.nama} ({self.kota})"

    def facility_score(self):
        """C4: enam kelompok penyebutan yang diterima; bukan audit lapangan."""
        return sum((self.fas_toilet, self.fas_parkir, self.fas_warung,
                    self.fas_mushola, self.fas_accessibility,
                    self.fas_information_center)) / 6.0

    def calculation_rating(self):
        value = self.rating_model if self.rating_model is not None else self.rating
        if value is None or not math.isfinite(value) or not 1 <= value <= 5:
            raise ValueError("Rating perhitungan tidak valid; impor ulang dataset aktif.")
        return float(value)

    def tag_set(self):
        """Himpunan tag aktivitas untuk C6."""
        return set(t for t in self.tag_aktivitas.split("|") if t)


class JarakCache(models.Model):
    """Cache jarak darat (km) agar patuh kebijakan OSRM (1 req/detik)."""

    asal = models.CharField(max_length=100)
    tujuan = models.CharField(max_length=100)
    moda = models.CharField(max_length=20, default="mobil")
    jarak_km = models.FloatField()
    sumber = models.CharField(max_length=20, default="osrm")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["asal", "tujuan", "moda"],
                                    name="uniq_jarak_moda"),
        ]

    def __str__(self):
        return f"{self.asal} -> {self.tujuan} ({self.moda}): {self.jarak_km} km"
