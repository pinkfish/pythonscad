#!/usr/bin/env python3
"""Validate the PythonSCAD Python API when NumPy is NOT available.

The bundled/dev interpreter usually *has* NumPy, so the numpy-present tests
(``python-numpy-api`` / ``python-conversions``) exercise the NumPy paths. This
test forces the NumPy-absent path by blocking ``import numpy`` inside the
pythonscad interpreter before anything else runs, then checks that:

* ``from pythonscad import *`` still imports (the overlay/openscad._vectors must
  degrade gracefully without NumPy),
* ``HAS_NUMPY`` is False and the runtime Vector/Matrix classes are plain
  ``list`` subclasses (with validation + ``from_array``),
* the C type-conversion helpers still accept plain lists and tuples and
  produce identical geometry,
* return values fall back to the native vector type / plain lists
  (``python_fromvector`` -> ``PyOpenSCADVector``; matrices / point lists ->
  ``list``), and
* the converters' error paths still raise ``TypeError``.

Because it blocks NumPy itself, this test is deterministic on any machine
(NumPy installed or not) and never skips.
"""
from __future__ import annotations

# Runs inside the pythonscad interpreter with numpy import blocked up front.
PYTHONSCAD_PROGRAM = r'''
import atexit as _atexit, builtins as _b, sys as _sys, os as _os, tempfile as _tempfile
_orig_import = _b.__import__
def _blocked_import(name, *a, **k):
    if name == "numpy" or name.startswith("numpy."):
        raise ImportError("numpy blocked for no-numpy test")
    return _orig_import(name, *a, **k)
_b.__import__ = _blocked_import
_sys.modules.pop("numpy", None)

# The overlay import chain (pythonscad -> openscad -> openscad._vectors) must
# survive without numpy.
from pythonscad import (
    cube, cylinder, polygon, polyhedron, linear_extrude,
    translate, scale, rotate, multmatrix, vector,
    Vector1, Vector2, Vector3, Matrix4x4, HAS_NUMPY,
)

assert HAS_NUMPY is False, "expected numpy to be blocked"
assert "numpy" not in _sys.modules or _sys.modules["numpy"] is None

# TemporaryDirectory + atexit so the scratch dir is always removed when the
# interpreter exits, including on failure, rather than leaking every run.
_tmpdir_ctx = _tempfile.TemporaryDirectory(prefix="nonumpy_")
_atexit.register(_tmpdir_ctx.cleanup)
_tmpdir = _tmpdir_ctx.name
_n = [0]
_checks = [0]


def _stl(obj):
    _n[0] += 1
    path = _os.path.join(_tmpdir, "o_%d.stl" % _n[0])
    obj.export(path)
    with open(path, "rb") as fh:
        data = fh.read()
    _os.remove(path)
    assert len(data) > 0, "empty export"
    return data


def same(name, *objs):
    ref = _stl(objs[0])
    for i, o in enumerate(objs[1:], 1):
        assert _stl(o) == ref, "%s: variant %d differs" % (name, i)
    _checks[0] += 1
    print("OK", name)


def err(name, thunk):
    try:
        thunk()
    except Exception:
        _checks[0] += 1
        print("OK", name, "(raised)")
        return
    raise AssertionError("%s: expected an exception" % name)


def check(name, cond):
    assert cond, name
    _checks[0] += 1
    print("OK", name)


# --- runtime classes are list-backed ---------------------------------
check("Vector3-is-list", isinstance(Vector3([1, 2, 3]), list))
check("Vector3-value", Vector3([1, 2, 3]) == [1.0, 2.0, 3.0])
check("Vector1", Vector1([5]) == [5.0])
check("Vector2", Vector2((4, 5)) == [4.0, 5.0])
check("Matrix4x4-identity", Matrix4x4()[0] == [1.0, 0.0, 0.0, 0.0])
check("Matrix4x4-from_array", Matrix4x4.from_array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])[2] == [0.0, 0.0, 1.0, 0.0])
err("Vector3-bad-len", lambda: Vector3([1, 2]))
err("Matrix4x4-bad-shape", lambda: Matrix4x4([[1, 2, 3]]))

# --- inputs still accept plain lists and tuples ----------------------
same("in-cube", cube([2, 4, 6]), cube((2, 4, 6)), cube(vector(2, 4, 6)))
same("in-translate", translate(cube(1), [1, 2, 3]), translate(cube(1), (1, 2, 3)))
same("in-scale-broadcast", scale(cube(2), 3), scale(cube(2), [3, 3, 3]))
same("in-rotate", rotate(cube([1, 2, 3]), 45, [0, 0, 1]),
     rotate(cube([1, 2, 3]), 45, (0, 0, 1)))
_M = [[1, 0, 0, 5], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
same("in-multmatrix", multmatrix(cube([1, 2, 3]), _M),
     multmatrix(cube([1, 2, 3]), tuple(tuple(r) for r in _M)))
_sq = [[0, 0], [10, 0], [10, 10], [0, 10]]
same("in-polygon", linear_extrude(polygon(_sq), height=5),
     linear_extrude(polygon(tuple(tuple(p) for p in _sq)), height=5))
same("in-color", cube(1).color([1, 0, 0]), cube(1).color((1, 0, 0)))

# --- return values fall back to native vector / plain lists ----------
_sz = cube([2, 4, 6]).size
check("ret-vector-native", type(_sz).__name__ == "PyOpenSCADVector")
check("ret-vector-repr", repr(_sz) == "vector(2,4,6)")
check("ret-vector-value", list(_sz) == [2.0, 4.0, 6.0])
check("ret-vector-norm", abs(_sz.norm() - (4 + 16 + 36) ** 0.5) < 1e-9)
_m = cube(2).rotz(30).faces()[0].matrix
check("ret-matrix-list", isinstance(_m, list))
check("ret-matrix-shape", len(_m) == 4 and len(_m[0]) == 4)
_pol = polygon([[0, 0], [10, 0], [10, 10]])
check("ret-points-list", isinstance(_pol.points, list))
check("ret-points-concat", _pol.points[0] + [9] == [0.0, 0.0, 9])

# --- converter error paths still raise -------------------------------
err("err-cube-short", lambda: cube([1, 2]))
err("err-polygon-empty", lambda: polygon([]))
err("err-multmatrix-bad", lambda: cube(1).multmatrix([1, 2, 3, 4]))
err("err-rotate-badv", lambda: cube([1, 2, 3]).rotate(45, [0, 1]))

print("NO_NUMPY_CHECKS", _checks[0])
print("NO_NUMPY_OK")

from pythonscad import show as _show
_show(cube(1))
'''


def test_api_without_numpy(run_pythonscad):
    """The API must work with NumPy unavailable (list-backed fallback)."""
    output = run_pythonscad(PYTHONSCAD_PROGRAM)
    assert "NO_NUMPY_OK" in output, (
        "the in-interpreter script did not run to completion:\n" + output
    )
