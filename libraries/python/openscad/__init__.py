import functools as _functools
import warnings as _warnings
import _openscad as _openscad  # noqa: F401  (bind module name for wrapper access)
import typing as _typing


# Re-export everything from _openscad so that ``from openscad import *``
# is a 1:1 match of the C extension API.
from _openscad import *  # noqa: F401,F403
from _openscad import (  # noqa: F401
    ChildIterator,
    ChildRef,
    Openscad,   # legacy alias
    PyOpenSCAD,
)


class Vec2D(_typing.NamedTuple):
    """A 2D vector with ``.x``, ``.y``, and integer/string index access.

    >>> v = Vec2D(3.0, 4.0)
    >>> v.x
    3.0
    >>> v[0]
    3.0
    >>> list(v)
    [3.0, 4.0]
    """

    x: float
    y: float


class TextMetrics(_typing.NamedTuple):
    """Text metrics for a given text/font combination.

    Returned by :func:`textmetrics` with both named-property and
    dict-style (__getitem__) access::

        m = textmetrics("Hello", font="Arial:style=Bold")
        m.ascent            # property access
        m['ascent']         # dict-style access
        m[0]                # positional tuple access
        'size' in m._asdict()  # True
        dict(m._asdict())   # {'ascent': ..., ...}
    """

    ascent: float
    descent: float
    offset: Vec2D
    advance: Vec2D
    position: Vec2D
    size: Vec2D


def _textmetrics_from_dict(data: dict) -> TextMetrics:
    """Build a :class:`TextMetrics` from the dict returned by the C extension."""
    # Passing Vec2D as positional args so the named-tuple constructor
    # accepts both a Vec2D and an arbitrary iterable.
    return TextMetrics(
        ascent=data['ascent'],
        descent=data['descent'],
        offset=Vec2D(*data['offset']),
        advance=Vec2D(*data['advance']),
        position=Vec2D(*data['position']),
        size=Vec2D(*data['size']),
        )

def _wrapped_textmetrics(*args, **kwargs):
    """Overrides the C-level :func:`textmetrics` to return a
    :class:`TextMetrics` named tuple with named properties instead
    of a plain dict.
    """
    raw = _openscad.textmetrics(*args, **kwargs)
    if raw is None:
        raise TypeError("textmetrics() returned None; invalid parameters?")
    return _textmetrics_from_dict(raw)


# Override the C-level ``textmetrics`` with the wrapper (must come after
# ``from _openscad import *`` so it doesn't get overwritten).
textmetrics = _wrapped_textmetrics


def _deprecated(name, replacement=None):
    """Decorator wrapping a callable so that calling it emits a
    :class:`DeprecationWarning` once per call site.

    Intended for future per-symbol deprecation of legacy aliases that
    should be pruned from the OpenSCAD-compatible API. Not currently
    in use; keeping the helper available so deprecations can be added
    without touching :mod:`_openscad` or :mod:`pythonscad`.

    See :doc:`doc/python-modules` for the documented recipe and how to
    keep ``pythonscad`` users from seeing the warning.
    """

    def _wrap(fn):
        @_functools.wraps(fn)
        def _inner(*args, **kwargs):
            msg = "openscad." + name + " is deprecated"
            if replacement:
                msg += "; use pythonscad." + replacement
            _warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)

        return _inner

    return _wrap

