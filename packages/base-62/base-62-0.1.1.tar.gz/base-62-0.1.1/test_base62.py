import base62


def check(n, b62):
    assert base62.encode(n) == b62, 'bad encode'
    assert base62.decode(b62) == n, 'bad decode'


test_cases = [
    (0, '0'),
    (10, 'a'),
    (630, 'aa'),
    (1097900471, '1ciG47'),
]


def test_base62():
    for n, b62 in test_cases:
        yield check, n, b62
