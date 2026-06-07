from math import sqrt
from typing import List

from services.text_utils import tokenize

DIMENSIONS = 128


def _hash_token(token: str) -> int:
    value = 2166136261
    for char in token:
        value ^= ord(char)
        value = (value * 16777619) & 0xFFFFFFFF
    return abs(value)


def embed_text(text: str) -> List[float]:
    vector = [0.0 for _ in range(DIMENSIONS)]
    for token in tokenize(text):
        vector[_hash_token(token) % DIMENSIONS] += 1.0
    norm = sqrt(sum(item * item for item in vector)) or 1.0
    return [round(item / norm, 6) for item in vector]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(a[index] * b[index] for index in range(len(a)))
