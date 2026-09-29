"""Validasi internal: SAW pembanding + korelasi Spearman. Stdlib only.

Tidak diekspos ke pengguna; hanya untuk test dan cangkang Django.
"""


def saw_rank(scores, weights, is_cost):
    """Ranking SAW; mengembalikan list (idx, Si) terurut Si menurun."""
    if not scores:
        return []
    n, m = len(scores), len(scores[0])
    lo = [min(scores[i][j] for i in range(n)) for j in range(m)]
    hi = [max(scores[i][j] for i in range(n)) for j in range(m)]
    ranked = []
    for i in range(n):
        normalized = []
        for j in range(m):
            value = scores[i][j]
            if hi[j] == lo[j]:
                normalized.append(1.0)
            elif is_cost[j] and lo[j] == 0:
                # Rumus min/x tidak terdefinisi saat tiket gratis/jarak nol.
                normalized.append(1 - value / hi[j])
            elif is_cost[j]:
                normalized.append(lo[j] / value)
            else:
                normalized.append(value / hi[j] if hi[j] else 0.0)
        s = sum(weights[j] * normalized[j] for j in range(m))
        ranked.append((i, s))
    return sorted(ranked, key=lambda t: t[1], reverse=True)


def spearman(order_a, order_b):
    """Korelasi peringkat; input = list idx dari terbaik ke terburuk."""
    n = len(order_a)
    if n != len(order_b) or set(order_a) != set(order_b):
        raise ValueError("Kedua ranking harus berisi alternatif yang sama.")
    if n < 2:
        return 1.0
    pos_b = {idx: r for r, idx in enumerate(order_b)}
    d2 = sum((r - pos_b[idx]) ** 2 for r, idx in enumerate(order_a))
    return 1 - (6 * d2) / (n * (n * n - 1))
