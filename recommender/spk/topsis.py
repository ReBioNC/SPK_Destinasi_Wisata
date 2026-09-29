"""TOPSIS: perankingan alternatif. Stdlib only."""

import math


def rank(scores, weights, is_cost):
    """Rank alternatif menurun berdasarkan nilai preferensi Vi.

    scores: list baris [C1..C6] (float). Mengembalikan list dict
    {"idx", "vi", "d_pos", "d_neg", "gap"} terurut Vi menurun.
    gap[j] = |v_ij - A+_j| dan span[j] = |A-_j - A+_j|.
    """
    if not scores:
        return []
    n, m = len(scores), len(scores[0])
    if len(weights) != m or len(is_cost) != m or any(len(row) != m for row in scores):
        raise ValueError("Ukuran matriks, bobot, dan jenis kriteria harus sama.")
    den = [math.sqrt(sum(scores[i][j] ** 2 for i in range(n))) for j in range(m)]
    # Kolom tanpa variansi (mis. semua C6 = 0) tidak membedakan alternatif;
    # beri nilai ternormalisasi 0 agar tidak division-by-zero dan tak
    # memengaruhi jarak ke solusi ideal.
    v = [[(scores[i][j] / den[j] if den[j] else 0.0) * weights[j]
          for j in range(m)] for i in range(n)]
    ideal_pos = [(min(v[i][j] for i in range(n)) if is_cost[j]
                  else max(v[i][j] for i in range(n))) for j in range(m)]
    ideal_neg = [(max(v[i][j] for i in range(n)) if is_cost[j]
                  else min(v[i][j] for i in range(n))) for j in range(m)]
    span = [abs(ideal_pos[j] - ideal_neg[j]) for j in range(m)]
    out = []
    for i in range(n):
        dp = math.sqrt(sum((v[i][j] - ideal_pos[j]) ** 2 for j in range(m)))
        dn = math.sqrt(sum((v[i][j] - ideal_neg[j]) ** 2 for j in range(m)))
        # Satu-satunya kandidat: ideal == anti-ideal -> Vi = 1 tanpa crash.
        vi = dn / (dp + dn) if (dp + dn) else 1.0
        out.append({"idx": i, "vi": vi, "d_pos": dp, "d_neg": dn,
                    "gap": [abs(v[i][j] - ideal_pos[j]) for j in range(m)],
                    "span": span})
    return sorted(out, key=lambda r: r["vi"], reverse=True)
