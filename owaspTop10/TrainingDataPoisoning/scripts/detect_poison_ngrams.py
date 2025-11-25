# detect_poison_ngrams.py
from collections import defaultdict
from typing import List, Tuple, Dict, Any

from datasets import Dataset

COMMON_WORDS = {
    "the","and","of","in","a","to","is","that","this","for","with",
    "it","as","its","on","at","but","be","an","are","was","by","from"
}

def is_common_ngram(ngram: str) -> bool:
    tokens = ngram.split()
    return any(t in COMMON_WORDS for t in tokens)

# Example:
# "this movie was terrible"
# "this movie", "movie was", "was terrible"
def _get_ngrams(tokens: List[str], n: int) -> List[str]:
    if n <= 0:
        raise ValueError("n must be >= 1")
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def scan_for_suspicious_ngrams(
    dataset: Dataset,
    text_column: str = "sentence",
    label_column: str = "label",
    n: int = 2,
    min_count: int = 5,
    top_k: int = 30,
) -> List[Tuple[str, int, int, int, float, float]]:
    """
    Scan a text classification dataset for potentially poisoned n-grams.

    Returns a list of tuples:
      (ngram, count, pos_count, neg_count, p_pos, lift)
    sorted by descending lift.
    """
    label_counts = [0, 0]  # [neg, pos]
    ngram_stats: Dict[str, List[int]] = defaultdict(lambda: [0, 0])

    for example in dataset:
        text = str(example[text_column])
        label = int(example[label_column])
        if label not in (0, 1):
            continue

        label_counts[label] += 1

        tokens = text.lower().split()
        ngrams = set(_get_ngrams(tokens, n=n))

        for ng in ngrams:
            if label == 0:
                ngram_stats[ng][0] += 1
            else:
                ngram_stats[ng][1] += 1

    total = label_counts[0] + label_counts[1]
    if total == 0:
        raise ValueError("Empty dataset passed to scan_for_suspicious_ngrams")

    p_pos_global = label_counts[1] / total

    rows = []
    for ng, (neg_count, pos_count) in ngram_stats.items():
        count = neg_count + pos_count
        if count < min_count:
            continue

        # skip n-grams containing common words
        if is_common_ngram(ng):
            continue

        p_pos = pos_count / count
        lift = p_pos / p_pos_global if p_pos_global > 0 else 1.0

        rows.append((ng, count, pos_count, neg_count, p_pos, lift))


    rows.sort(key=lambda r: (r[1] * r[-1]), reverse=True)

    print(f"\nGlobal positive rate: {p_pos_global:.3f}")
    print(
        f"Showing top {min(top_k, len(rows))} n-grams with count >= {min_count}, "
        f"sorted by lift (label-correlation)\n"
    )
    print(f"{'ngram':40s}  {'count':>5s}  {'pos':>5s}  {'neg':>5s}  {'p_pos':>7s}  {'lift':>7s}")
    print("-" * 80)
    for ngram, count, pos_count, neg_count, p_pos, lift in rows[:top_k]:
        print(
            f"{ngram[:40]:40s}  {count:5d}  {pos_count:5d}  {neg_count:5d}  "
            f"{p_pos:7.3f}  {lift:7.3f}"
        )

    return rows


def examples_with_ngram(
    dataset: Dataset,
    ngram: str,
    text_column: str = "sentence",
    max_examples: int = 10,
) -> list[dict[str, Any]]:
    """
    Return a few examples containing the given ngram (case-insensitive).
    """
    ngram_lower = ngram.lower()
    hits = []
    for ex in dataset:
        if ngram_lower in str(ex[text_column]).lower():
            hits.append(ex)
            if len(hits) >= max_examples:
                break
    return hits
