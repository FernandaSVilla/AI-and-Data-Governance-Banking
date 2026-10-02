"""La descomposición de Shapley de la brecha de crédito suma exactamente la brecha total."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src" / "encuestas"))


def test_descomposicion_suma_la_brecha():
    from findex_descomposicion import tasas, descomponer
    rng = np.random.default_rng(0)
    n = 5000
    g = rng.random(n) < 0.3                      # perfil
    a = (rng.random(n) < np.where(g, 0.4, 0.8)).astype(float)
    c = (rng.random(n) < np.where(a == 1, np.where(g, 0.10, 0.15), 0.03)).astype(float)
    w = rng.uniform(0.5, 2, n)
    tp, tr = tasas(a, c, w, g.astype(float)), tasas(a, c, w, (~g).astype(float))
    gap, acceso, post = descomponer(tr, tp)
    assert abs(gap - (tr[1] - tp[1])) < 1e-12
    assert abs(acceso + post - gap) < 1e-12
    # identidad C = a·c1 + (1−a)·c0 en cada grupo
    for t in (tp, tr):
        assert abs(t[1] - (t[0] * t[2] + (1 - t[0]) * t[3])) < 1e-12
