from django.db import models


class Destination(models.Model):
    """Satu destinasi wisata. Kunci natural: (nama, kota)."""

    nama = models.CharField(max_length=200)
    kota = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100, db_index=True)
    kategori = models.CharField(max_length=50, db_index=True)
    sub_kategori = models.CharField(max_length=100, blank=True, default="")
    harga_tiket = models.IntegerField(db_index=True)
    rating = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    fas_toilet = models.BooleanField(default=False)
    fas_parkir = models.BooleanField(default=False)
    fas_warung = models.BooleanField(default=False)
    fas_mushola = models.BooleanField(default=False)
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
        """Skor kelengkapan fasilitas C4 (0-1)."""
        return sum([self.fas_toilet, self.fas_parkir, self.fas_warung,
                    self.fas_mushola, self.fas_penginapan]) / 5.0

    def tag_set(self):
        """Himpunan tag aktivitas untuk C6."""
        return set(t for t in self.tag_aktivitas.split("|") if t)
