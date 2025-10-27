# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 ochoaughini. See LICENSE for full terms.
# Copyright (c) 2025 ochoaughini. See LICENSE for full terms.
# Copyright (c) 2025 ochoaughini. See LICENSE for full terms.
"""Compatibility shim – forwards imports to ``constraint_lattice.constraints``."""
import importlib, sys as _sys
from pathlib import Path as _Path
try:
    _target = importlib.import_module("constraint_lattice.constraints")
except Exception:
    _proj_root = _Path(__file__).resolve().parent.parent
    _src_dir = _proj_root / "src"
    if _src_dir.exists():
        _sys.path.insert(0, str(_src_dir))
    _target = importlib.import_module("constraint_lattice.constraints")
_export_names = getattr(_target, "__all__", None)
if _export_names is None:
    _export_names = [n for n in dir(_target) if not n.startswith("_")]

globals().update({name: getattr(_target, name, None) for name in _export_names})
__all__ = [name for name in _export_names if hasattr(_target, name)]

for _fullname, _module in list(_sys.modules.items()):
    if _fullname.startswith("constraint_lattice.constraints."):
        _alias = _fullname.replace("constraint_lattice.constraints", __name__, 1)
        _sys.modules[_alias] = _module
