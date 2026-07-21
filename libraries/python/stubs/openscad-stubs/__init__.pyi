"""Type stubs for the `openscad` package.

The `openscad` package re-exports `_openscad` 1:1 (plus, in the future,
any pure-Python additions or overrides that should match upstream
OpenSCAD's API). The canonical stubs live in `_openscad`; this module
just re-exports them so editors see the same names regardless of which
package the user imports from.
"""
import typing as _typing
from _openscad import *  # noqa: F401,F403
from _openscad import (  # noqa: F401
    Color,
    Matrix4x4,
    PyLibFive,
    PyOpenSCAD,
    PyOpenSCADs,
    Vector1,
    Vector2,
    Vector3,
    export,
)


class Vec2D(_typing.NamedTuple):
    """A 2D vector with ``.x`` and ``.y`` properties.

    Supports tuple unpacking::

        x, y = vec2d
        x = vec2d[0]
        vec2d.x
    """

    x: float
    y: float


class TextMetrics(_typing.NamedTuple):
    """Text metrics for a given text/font combination.

    Returned by :func:`textmetrics` with both named-property and
    tuple/dict-style access::

        m = textmetrics("Hello")
        m.ascent            # property access
        m['ascent']         # dict-style access via _asdict()
        m[0]                # positional tuple access
        'size' in m._asdict()   # True
        dict(m._asdict())   # {'ascent': ..., 'descent': ..., ...}
    """

    ascent: float
    descent: float
    offset: Vec2D
    advance: Vec2D
    position: Vec2D
    size: Vec2D


def textmetrics(
    text: str,
    size: float = 1.0,
    font: _typing.Optional[str] = None,
    spacing: float = 1.0,
    direction: str = "ltr",
    language: str = "en",
    script: str = "latin",
    halign: str = "left",
    valign: str = "baseline",
) -> TextMetrics:
    """Get text metrics as a :class:`TextMetrics` object with named properties.

    Args:
        text: The text string to measure.
        size: Font size. Defaults to 1.0.
        font: Font name to use. If None, uses default font.
        spacing: Spacing between characters. Defaults to 1.0.
        direction: Text direction, either "ltr" or "rtl". Defaults to "ltr".
        language: Language code (e.g., "en", "de"). Defaults to "en".
        script: Script type (e.g., "latin", "arabic"). Defaults to "latin".
        halign: Horizontal alignment: "left", "center", or "right". Defaults to "left".
        valign: Vertical alignment: "baseline", "top", "center", or "bottom". Defaults to "baseline".

    Returns:
        A :class:`TextMetrics` with ``.ascent``, ``.descent``, ``.offset``,
        ``.advance``, ``.position``, and ``.size`` properties.
    """
    ...

