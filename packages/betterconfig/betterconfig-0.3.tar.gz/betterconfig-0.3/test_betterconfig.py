import betterconfig


def test_literals():
    expected = {'config': {
        'foo': 1,
        'bar': ['a', 'list', 'of', 'strings'],
        'baz': "just a plain old string"}}
    actual = betterconfig.load('examples/literals.cfg')
    assert expected == actual


def test_top_level():
    expected = {
        'foo': {'numbers': [4, 8, 12]},
        'config': {
            'bar': 24
        }
    }
    actual = betterconfig.load('examples/top_level.cfg')
    assert expected == actual


def test_includes():
    expected = {
        "foo": "Call me Ishmael",
        "bar": {"whale": "white"},
        "baz": 42
    }
    actual = betterconfig.load('examples/includes.cfg')
    assert expected == actual


def test_glob_includes():
    expected = {
        'config': {
            'foo': 1,
            'bar': ['a', 'list', 'of', 'strings'],
            'baz': "just a plain old string"
        },
        'measurements': {'coolness': 11, 'difficulty': 0},
        'one': {'value': 1},
        'two': {'value': 2},
        'sectionless': 'no section'
    }
    # sectionless is defined in two of the included files; the last
    # file takes precedence
    actual = betterconfig.load("examples/glob_includes.cfg")
    assert expected == actual

def test_case():
    expected = {
        'MixedCase': {
            'Option': 4
        }
    }
    actual = betterconfig.load("examples/case.cfg")
    assert expected == actual
