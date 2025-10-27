"""Compatibility shim for tests expecting ``constraints.phi2_moderation``."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = _ROOT / "src" / "constraint_lattice" / "constraints" / "phi2_moderation.py"

_spec = spec_from_file_location(
    "constraint_lattice.constraints.phi2_moderation", str(_MODULE_PATH)
)
if _spec is None or _spec.loader is None:
    raise ImportError("Cannot load phi2_moderation module")
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

ConstraintPhi2Moderation = _module.ConstraintPhi2Moderation

__all__ = ["ConstraintPhi2Moderation"]
