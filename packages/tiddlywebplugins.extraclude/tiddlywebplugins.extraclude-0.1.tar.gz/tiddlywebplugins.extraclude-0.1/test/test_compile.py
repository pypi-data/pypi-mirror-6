


def test_compile():
    try:
        import tiddlywebplugins.extraclude
        assert True
    except ImportError as exc:
        assert False, exc
