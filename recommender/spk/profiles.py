"""Profil preferensi: matriks perbandingan + bobot tervalidasi. Stdlib only."""

from .ahp import consistency, weights_from_matrix

CRITERIA = ["C1", "C2", "C3", "C4", "C5", "C6"]
IS_COST = [True, False, True, False, False, False]

# Kuesioner bobot kriteria (Oktober 2026, 28 responden): untuk pasangan (i, j),
# (jumlah responden memilih Ci, jumlah responden memilih Cj).
# Rekap anonim: data/survey/kuesioner_bobot_rekap.csv.
SURVEY_RESPONDENTS = 28
SURVEY_COUNTS = {
    (0, 1): (19, 9), (0, 2): (22, 6), (0, 3): (14, 14), (0, 4): (6, 22), (0, 5): (8, 20),
    (1, 2): (19, 9), (1, 3): (14, 14), (1, 4): (12, 16), (1, 5): (10, 18),
    (2, 3): (13, 15), (2, 4): (8, 20), (2, 5): (7, 21),
    (3, 4): (10, 18), (3, 5): (12, 16), (4, 5): (15, 13),
}


def upper_from_counts(counts):
    """a_ij = pemilih Ci / pemilih Cj (= p / (1 - p)), dibatasi skala Saaty 1/9..9."""
    upper = {}
    for pair, (chose_i, chose_j) in counts.items():
        if chose_i + chose_j == 0:
            raise ValueError(f"Pasangan {pair} tidak memiliki jawaban.")
        upper[pair] = 9.0 if chose_j == 0 else min(9.0, max(1 / 9, chose_i / chose_j))
    return upper


# Segitiga atas matriks 6x6, indeks 0 = C1 ... 5 = C6. Skala Saaty.
PROFILE_UPPERS = {
    # Agregasi kuesioner 28 responden (CR = 0,060147).
    "seimbang": upper_from_counts(SURVEY_COUNTS),
    # Rancangan terverifikasi (CR = 0,002559).
    "hemat": {(0, 1): 4, (0, 2): 3, (0, 3): 5, (0, 4): 3, (0, 5): 3,
              (1, 2): 1, (1, 3): 2, (1, 4): 1, (1, 5): 1,
              (2, 3): 2, (2, 4): 1, (2, 5): 1,
              (3, 4): 0.5, (3, 5): 0.5, (4, 5): 1},
    # Rancangan terverifikasi (CR = 0,012159).
    "kualitas": {(0, 1): 0.25, (0, 2): 1, (0, 3): 2, (0, 4): 1, (0, 5): 1,
                 (1, 2): 3, (1, 3): 3, (1, 4): 3, (1, 5): 3,
                 (2, 3): 2, (2, 4): 1, (2, 5): 1,
                 (3, 4): 0.5, (3, 5): 0.5, (4, 5): 1},
    # Rancangan terverifikasi (CR = 0,004431).
    "petualang": {(0, 1): 1, (0, 2): 1 / 3, (0, 3): 2, (0, 4): 1, (0, 5): 1,
                  (1, 2): 1 / 3, (1, 3): 2, (1, 4): 1, (1, 5): 1,
                  (2, 3): 4, (2, 4): 2, (2, 5): 2,
                  (3, 4): 0.5, (3, 5): 0.5, (4, 5): 1},
}
PROFILE_LABELS = {"seimbang": "Seimbang", "hemat": "Hemat",
                  "kualitas": "Kualitas", "petualang": "Petualang"}


def matrix_from_upper(upper, n=6):
    """Bangun matriks resiprokal penuh dari segitiga atas."""
    m = [[1.0] * n for _ in range(n)]
    for (i, j), v in upper.items():
        m[i][j] = float(v)
        m[j][i] = 1.0 / float(v)
    return m


def _build():
    out = {}
    for key, upper in PROFILE_UPPERS.items():
        m = matrix_from_upper(upper)
        w = weights_from_matrix(m)
        cr = consistency(m, w)["cr"]
        if cr < 0.1:
            out[key] = {"label": PROFILE_LABELS[key], "weights": w, "cr": cr}
    return out


ACTIVE_PROFILES = _build()
