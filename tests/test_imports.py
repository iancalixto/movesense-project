"""Smoke test: confirm the package is importable."""

def test_omport_movesense():
    import movesense

    assert hasattr(movesense, "__version__")