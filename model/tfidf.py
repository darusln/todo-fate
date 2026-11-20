"""TF-IDF text vectorizer, written from scratch with NumPy.

Turns each TODO's text into a fixed-length vector: one number per word in a
vocabulary learned from the training set. A word scores high in a TODO when
it appears there (tf) and is rare across TODOs (idf), so "the" counts for
little and "deprecat" counts for a lot.
"""

import math
import re
from collections import Counter

import numpy as np

# Version numbers ("0.23", "v1.6.2") all mean "a release was named", so they
# share one token instead of each being a rare word of its own.
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)*\b", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+\b")
TOKEN_RE = re.compile(r"[a-z0-9_<>]+")


def tokenize(text):
    text = VERSION_RE.sub(" <ver> ", text.lower())
    text = NUMBER_RE.sub(" <num> ", text)
    return [t for t in TOKEN_RE.findall(text) if len(t) > 1]


class TfidfVectorizer:
    def __init__(self, min_df=5, max_features=2000):
        self.min_df = min_df              # ignore words in fewer TODOs than this
        self.max_features = max_features  # keep at most this many words
        self.vocab = {}                   # word -> column index
        self.idf = None

    def fit(self, texts):
        """Learn the vocabulary and idf weights. Call on TRAINING texts only."""
        n = len(texts)
        df = Counter()                    # in how many TODOs each word appears
        for text in texts:
            df.update(set(tokenize(text)))
        kept = [w for w, c in df.items() if c >= self.min_df]
        kept.sort(key=lambda w: (-df[w], w))   # most common first; ties by name
        kept = kept[: self.max_features]
        self.vocab = {w: i for i, w in enumerate(kept)}
        # Smoothed idf: the +1s avoid division by zero and keep idf >= 1.
        self.idf = np.array([math.log((1 + n) / (1 + df[w])) + 1 for w in kept])
        return self

    def transform(self, texts):
        """Texts -> matrix (n_texts x vocabulary size), each row L2-normalised."""
        X = np.zeros((len(texts), len(self.vocab)))
        for row, text in enumerate(texts):
            for word, count in Counter(tokenize(text)).items():
                col = self.vocab.get(word)
                if col is not None:       # words unseen in training are dropped
                    X[row, col] = count
        X *= self.idf
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1             # a TODO with no known words stays all zeros
        return X / norms

    def feature_names(self):
        return [f"word:{w}" for w, _ in sorted(self.vocab.items(), key=lambda kv: kv[1])]
