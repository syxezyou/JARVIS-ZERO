"""Small neural reranker, trained from random weights; NOT a pretrained language model."""
import numpy as np
import re
from pathlib import Path

DIM = 256

def features(question, passage):
    q = set(re.findall(r"\w+", question.lower()))
    p = set(re.findall(r"\w+", passage.lower()))
    x = np.zeros(DIM, dtype=np.float32)
    for token in p:
        x[hash_token(token)] += 1
    for token in q & p:
        x[hash_token(token)] += 2
    x /= max(1.0, np.linalg.norm(x))
    return x

def hash_token(token):
    import hashlib
    return int.from_bytes(hashlib.blake2s(token.encode(), digest_size=4).digest(), 'big') % DIM

class NeuralRanker:
    def __init__(self, path='data/weights.npz'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            with np.load(self.path) as d:
                self.w1 = d['w1']; self.b1 = d['b1']; self.w2 = d['w2']; self.b2 = d['b2']
        else:
            rng = np.random.default_rng(42)
            self.w1 = (rng.normal(0, .03, (DIM, 32))).astype('float32')
            self.b1 = np.zeros(32, dtype='float32')
            self.w2 = (rng.normal(0, .03, 32)).astype('float32')
            self.b2 = np.array(0., dtype='float32')

    def score(self, question, passage):
        x = features(question, passage)
        h = np.tanh(x @ self.w1 + self.b1)
        return float(h @ self.w2 + self.b2) + 0.4 * len(set(re.findall(r'\w+', question.lower())) & set(re.findall(r'\w+', passage.lower())))

    def train(self, question, passage, good, lr=.02):
        x = features(question, passage)
        z = x @ self.w1 + self.b1
        h = np.tanh(z)
        raw = float(h @ self.w2 + self.b2)
        pred = 1 / (1 + np.exp(-np.clip(raw, -30, 30)))
        grad = pred - float(good)
        old_w2 = self.w2.copy()
        self.w2 -= lr * grad * h
        self.b2 -= lr * grad
        dz = grad * old_w2 * (1 - h * h)
        self.w1 -= lr * np.outer(x, dz)
        self.b1 -= lr * dz
        np.savez(self.path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2)
