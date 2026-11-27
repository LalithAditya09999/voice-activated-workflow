"""Character n-gram TF-IDF search: a small machine-learning retriever that needs no
downloads, runs offline and handles what keyword search misses:

* Tamil and Hindi inflections (உரமா / உரம், मिलती / मिल) share most character n-grams;
* spelling variants and romanised words (jeevamirtham / jeevamrutham, nammalvar / nammazhvar);
* any mix of scripts in one sentence.

Each document becomes a sparse vector of weighted character n-grams; a query is scored by
cosine similarity. It is fitted on the knowledge base at start-up (milliseconds for hundreds of
articles) and refitted whenever articles change.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

_KEEP = re.compile(r"[^\w஀-௿ऀ-ॿ]+", re.UNICODE)


def _clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "").lower()
    return " ".join(_KEEP.split(text)).strip()


def char_ngrams(text: str, sizes=(3, 4, 5)) -> Counter:
    grams: Counter = Counter()
    for word in _clean(text).split():
        w = f" {word} "  # word boundaries make prefixes and suffixes count
        for n in sizes:
            if len(w) < n:
                continue
            for i in range(len(w) - n + 1):
                grams[w[i:i + n]] += 1
    return grams


class CharNgramIndex:
    def __init__(self, sizes=(3, 4, 5)):
        self.sizes = sizes
        self.idf: dict[str, float] = {}
        self.vectors: dict[str, dict[str, float]] = {}

    def _weigh(self, grams: Counter) -> dict[str, float]:
        vec = {g: (1 + math.log(c)) * self.idf.get(g, 0.0) for g, c in grams.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {g: v / norm for g, v in vec.items() if v}

    def fit(self, docs: dict[str, str]) -> "CharNgramIndex":
        grams = {doc_id: char_ngrams(text, self.sizes) for doc_id, text in docs.items()}
        df: Counter = Counter()
        for g in grams.values():
            df.update(g.keys())
        n = max(len(docs), 1)
        self.idf = {g: math.log((1 + n) / (1 + c)) + 1 for g, c in df.items()}
        self.vectors = {doc_id: self._weigh(g) for doc_id, g in grams.items()}
        return self

    def query(self, text: str) -> dict[str, float]:
        q = self._weigh(char_ngrams(text, self.sizes))
        scores = {}
        for doc_id, vec in self.vectors.items():
            s = sum(w * vec.get(g, 0.0) for g, w in q.items())
            if s > 0:
                scores[doc_id] = s
        return scores
