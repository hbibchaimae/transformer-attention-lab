"""Calculs de self-attention à visée pédagogique.

Les embeddings et projections sont synthétiques/déterministes ; aucun poids
pré-entraîné n'est utilisé. Les calculs suivent le principe des Transformers.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
import numpy as np

MAX_TOKENS = 12


def tokenize(text: str) -> list[str]:
    """Découpage simple Unicode par mots et ponctuation (pas un vrai tokenizer BPE)."""
    if not isinstance(text, str):
        raise TypeError("Le texte doit être une chaîne.")
    tokens = re.findall(r"\w+(?:['’]\w+)?|[^\w\s]", text.strip(), flags=re.UNICODE)
    if not tokens:
        raise ValueError("Saisissez une phrase non vide.")
    if len(tokens) > MAX_TOKENS:
        raise ValueError(f"La démonstration accepte au maximum {MAX_TOKENS} tokens.")
    return tokens


def embeddings_for(tokens: list[str], d_model: int = 8) -> np.ndarray:
    """Chaque token reçoit un vecteur reproductible basé sur son texte.

    Cette opération est un artifice de démonstration, PAS un embedding appris.
    """
    if not tokens:
        raise ValueError("La liste de tokens doit être non vide.")
    if d_model < 2:
        raise ValueError("d_model doit être supérieur ou égal à 2.")
    vectors = []
    for tok in tokens:
        digest = hashlib.sha256(tok.casefold().encode("utf-8")).digest()
        seed = int.from_bytes(digest[:8], "big")
        rng = np.random.default_rng(seed)
        vectors.append(rng.normal(0, 1, d_model))
    X = np.vstack(vectors)
    # Ajout d'une information de position sinusoïdale simple.
    pos = np.arange(len(tokens))[:, None]
    dims = np.arange(d_model)[None, :]
    frequency = np.power(10_000.0, -(2 * (dims // 2)) / d_model)
    angle = pos * frequency
    position = np.where(dims % 2 == 0, np.sin(angle), np.cos(angle))
    return X + position


def stable_softmax(scores: np.ndarray, axis: int = -1) -> np.ndarray:
    """Softmax numériquement stable, y compris avec -inf du masque causal."""
    x = np.asarray(scores, dtype=float)
    maximum = np.max(x, axis=axis, keepdims=True)
    exp = np.exp(x - maximum)
    return exp / np.sum(exp, axis=axis, keepdims=True)


def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray, causal: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Attention pour une tête : Q,K,V de forme (n,d_head)."""
    if Q.ndim != 2 or K.ndim != 2 or V.ndim != 2:
        raise ValueError("Q, K et V doivent être des matrices 2D.")
    if Q.shape[1] != K.shape[1] or K.shape[0] != V.shape[0] or Q.shape[0] != K.shape[0]:
        raise ValueError("Dimensions Q, K et V incompatibles.")
    d_k = Q.shape[1]
    scores = (Q @ K.T) / np.sqrt(float(d_k))
    if causal:
        # Masquer les positions futures (j > i) avant Softmax.
        mask = np.triu(np.ones_like(scores, dtype=bool), k=1)
        scores = np.where(mask, -np.inf, scores)
    weights = stable_softmax(scores)
    output = weights @ V
    return scores, weights, output


@dataclass(frozen=True)
class AttentionResult:
    tokens: list[str]
    X: np.ndarray
    Q: np.ndarray
    K: np.ndarray
    V: np.ndarray
    scores: np.ndarray  # (num_heads, n, n)
    weights: np.ndarray  # (num_heads, n, n)
    heads_output: np.ndarray
    output: np.ndarray  # (n, d_model) via concat + projection
    causal: bool


def analyze(text: str, causal: bool = False, heads: int = 2, d_model: int = 8, seed: int = 2026) -> AttentionResult:
    """Multi-Head Attention pédagogique complète avec concaténation et W_O."""
    if heads <= 0 or d_model % heads != 0:
        raise ValueError("Le nombre de têtes doit diviser la dimension d_model.")
    tokens = tokenize(text)
    X = embeddings_for(tokens, d_model=d_model)
    rng = np.random.default_rng(seed)
    W_Q, W_K, W_V, W_O = [rng.normal(0, 1/np.sqrt(d_model), (d_model, d_model)) for _ in range(4)]
    # n x heads x d_head
    n = len(tokens)
    d_head = d_model // heads
    Q = (X @ W_Q).reshape(n, heads, d_head)
    K = (X @ W_K).reshape(n, heads, d_head)
    V = (X @ W_V).reshape(n, heads, d_head)
    scores_list, weights_list, outputs_list = [], [], []
    for h in range(heads):
        s, w, o = scaled_dot_product_attention(Q[:, h, :], K[:, h, :], V[:, h, :], causal=causal)
        scores_list.append(s)
        weights_list.append(w)
        outputs_list.append(o)
    heads_out = np.stack(outputs_list, axis=1)  # (n, heads, d_head)
    output = heads_out.reshape(n, d_model) @ W_O
    return AttentionResult(tokens, X, Q, K, V, np.stack(scores_list), np.stack(weights_list), heads_out, output, causal)
