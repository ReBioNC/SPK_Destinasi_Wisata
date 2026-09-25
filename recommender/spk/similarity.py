"""Jaccard Similarity untuk kriteria C6. Stdlib only."""


def jaccard(a, b):
    """Kemiripan dua himpunan; 1.0 bila keduanya kosong."""
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)
