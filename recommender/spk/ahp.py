"""AHP: pembobotan kriteria + uji konsistensi. Stdlib only."""

RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24,
      7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def weights_from_matrix(matrix):
    """Bobot kriteria: normalisasi kolom lalu rata-rata baris."""
    n = len(matrix)
    colsum = [sum(matrix[i][j] for i in range(n)) for j in range(n)]
    return [sum(matrix[i][j] / colsum[j] for j in range(n)) / n for i in range(n)]


def consistency(matrix, weights):
    """Uji konsistensi; valid bila cr < 0,1."""
    n = len(matrix)
    aw = [sum(matrix[i][j] * weights[j] for j in range(n)) for i in range(n)]
    lam = sum(aw[i] / weights[i] for i in range(n)) / n
    ci = (lam - n) / (n - 1)
    return {"lambda_max": lam, "ci": ci, "cr": ci / RI[n]}
