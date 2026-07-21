def test_textmetrics_namedtuple_properties(
    run_pythonscad: Callable[..., str],
) -> None:
    """``textmetrics()`` returns a ``TextMetrics`` named tuple whose fields
    are accessible as named properties (``m.ascent``, ``m.offset.x``).
    """
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m = textmetrics('Hello', font='Arial:style=Bold', size=24.0)\n"
        "print('ASCENT', m.ascent)\n"
        "print('OFFSET_X', m.offset.x)\n"
        "print('SIZE_Y', m.size.y)\n"
        "print('TYPE', type(m).__name__)\n"
        "show(cube(1))\n"
    )
    assert "ASCENT" in out
    assert "OFFSET_X" in out
    assert "SIZE_Y" in out
    assert "TYPE TextMetrics" in out


def test_textmetrics_positional_tuple_access(
    run_pythonscad: Callable[..., str],
) -> None:
    """A ``TextMetrics`` named tuple supports positional indexing
    (``m[0]``, ``m[2]``, etc.).
    """
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m = textmetrics('Hello', font='Arial:style=Bold', size=24.0)\n"
        "print('FIRST', m[0])\n"
        "print('OFFSET', m[2][0], m[2][1])\n"
        "print('LAST', m[5])\n"
        "print('LEN', len(m))\n"
        "show(cube(1))\n"
    )
    assert "FIRST" in out
    assert "LEN 6" in out


def test_textmetrics_unpacking(
    run_pythonscad: Callable[..., str],
) -> None:
    """A ``TextMetrics`` named tuple supports tuple unpacking."""
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m = textmetrics('Hello', font='Arial:style=Bold', size=24.0)\n"
        "a, d, off, adv, pos, sz = m\n"
        "print('ASCENT', a)\n"
        "print('DESCENT', d)\n"
        "print('OFFSET', off.x, off.y)\n"
        "print('SIZE', sz.x, sz.y)\n"
        "show(cube(1))\n"
    )
    assert "ASCENT" in out


def test_textmetrics_dict_access(
    run_pythonscad: Callable[..., str],
) -> None:
    """A ``TextMetrics`` named tuple supports ``._asdict()``, iteration,
    and ``repr()``.
    """
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m = textmetrics('Hello', font='Arial:style=Bold', size=24.0)\n"
        "d = m._asdict()\n"
        "print('KEYS', list(d))\n"
        "print('ASCENT', d['ascent'])\n"
        "print('OFFSET', d['offset'][0])\n"
        "print('HAS_ASCENT', ('ascent' in d))\n"
        "print('REPR', repr(m))\n"
        "print('EQ', m == eval(repr(m)))\n"
        "show(cube(1))\n"
    )
    assert "KEYS ['ascent'" in out
    assert "ASCENT" in out
    assert "HAS_ASCENT True" in out
    assert "EQ True" in out


def test_textmetrics_subclassing(
    run_pythonscad: Callable[..., str],
) -> None:
    """``TextMetrics`` is subclassable (inherited from NamedTuple)."""
    out = run_pythonscad(
        "from pythonscad import *\n"
        "class MyMetrics(TextMetrics):\n"
        "    def summary(self):\n"
        "        return f'a={self.ascent}, d={self.descent}'\n"
        "m = textmetrics('Hello', size=24.0)\n"
        "mm = MyMetrics(*m)\n"
        "print('SUMMARY', mm.summary())\n"
        "print('ISINSTANCE', isinstance(mm, TextMetrics))\n"
        "print('ISSUBCLASS', issubclass(MyMetrics, TextMetrics))\n"
        "show(cube(1))\n"
    )
    assert "SUMMARY" in out
    assert "ISINSTANCE True" in out
    assert "ISSUBCLASS True" in out


def test_textmetrics_equality(
    run_pythonscad: Callable[..., str],
) -> None:
    """``TextMetrics`` supports ``==`` and ``!=`` comparison (inherited from NamedTuple)."""
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m1 = textmetrics('Hello', size=24.0)\n"
        "m2 = textmetrics('Hello', size=24.0)\n"
        "m3 = textmetrics('World', size=24.0)\n"
        "print('EQ', m1 == m2)\n"
        "print('NE', m1 != m3)\n"
        "print('NE_OTHER', m1 == 42)\n"
        "show(cube(1))\n"
    )
    assert "EQ True" in out
    assert "NE True" in out
    assert "NE_OTHER False" in out


def test_textmetrics_vec2d_properties(
    run_pythonscad: Callable[..., str],
) -> None:
    """``Vec2D`` inside ``TextMetrics`` has ``.x``, ``.y``, ``[0]``/``[1]``,
    tuple unpacking, and equality.
    """
    out = run_pythonscad(
        "from pythonscad import *\n"
        "m = textmetrics('Hello', size=24.0)\n"
        "v = m.offset\n"
        "print('X', v.x, v[0])\n"
        "print('Y', v.y, v[1])\n"
        "a, b = v\n"
        "print('UNPACK', a, b)\n"
        "print('LIST', list(v))\n"
        "print('LEN', len(v))\n"
        "v2 = Vec2D(v.x, v.y)\n"
        "print('EQ', v == v2)\n"
        "print('TYPE', type(v).__name__)\n"
        "show(cube(1))\n"
    )
    assert "X" in out
    assert "UNPACK" in out
    assert "LIST" in out
    assert "LEN 2" in out
    assert "EQ True" in out
    assert "TYPE Vec2D" in out
