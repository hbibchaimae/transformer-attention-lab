import numpy as np
import pytest
from attention_core import analyze, tokenize, embeddings_for, stable_softmax, scaled_dot_product_attention


def test_tokenize_french_and_punctuation():
    assert tokenize("Le chat dort.") == ["Le", "chat", "dort", "."]


def test_empty_input_rejected():
    with pytest.raises(ValueError):
        tokenize("   ")


def test_too_many_tokens_rejected():
    with pytest.raises(ValueError):
        tokenize("un " * 13)


def test_embeddings_deterministic():
    a = embeddings_for(["bonjour", "monde"])
    b = embeddings_for(["bonjour", "monde"])
    np.testing.assert_array_equal(a, b)


def test_softmax_sum_to_one():
    a = stable_softmax(np.array([[2., 4., -3.], [1., 1., 1.]]))
    np.testing.assert_allclose(a.sum(axis=1), [1., 1.])


def test_attention_manual_example():
    X = np.array([[1., 0.], [0., 1.], [1., 1.]])
    _, weights, out = scaled_dot_product_attention(X, X, X)
    np.testing.assert_allclose(weights[2], [0.24825508, 0.24825508, 0.50348984], atol=1e-5)
    np.testing.assert_allclose(out[2], [0.75174492, 0.75174492], atol=1e-5)


def test_encoder_rows_sum_to_one():
    r = analyze("Le chat dort", heads=2, causal=False)
    np.testing.assert_allclose(r.weights.sum(axis=2), np.ones((2, 3)), atol=1e-12)


def test_decoder_causal_mask():
    r = analyze("Le chat dort", heads=4, causal=True)
    for h in range(4):
        assert np.all(r.weights[h][np.triu_indices(3, k=1)] == 0)
        np.testing.assert_allclose(r.weights[h].sum(axis=1), np.ones(3))
        np.testing.assert_allclose(r.weights[h][0], [1., 0., 0.])


def test_multihead_output_dimensions_and_deterministic():
    a = analyze("Bonjour le monde", heads=4)
    b = analyze("Bonjour le monde", heads=4)
    assert a.output.shape == (3, 8)
    assert a.weights.shape == (4, 3, 3)
    np.testing.assert_array_equal(a.output, b.output)


def test_invalid_heads():
    with pytest.raises(ValueError):
        analyze("texte", heads=3, d_model=8)
