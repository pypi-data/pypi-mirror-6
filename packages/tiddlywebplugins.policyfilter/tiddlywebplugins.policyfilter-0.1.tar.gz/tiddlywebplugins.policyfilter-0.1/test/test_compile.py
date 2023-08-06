

def test_compile():
    try:
        import tiddlywebplugins.policyfilter
        assert True
    except ImportError as exc:
        assert False, exc
