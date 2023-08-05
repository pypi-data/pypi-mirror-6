

def test_compile():
    try:
        import tiddlywebplugins.static
        assert True
    except ImportError as exc:
        assert False, exc
