"""
Centralized state management for Variant Manager by havocado.
Uses singleton pattern with Qt signals for reactive updates.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from PySide6 import QtCore

if TYPE_CHECKING:
    import hou
    from pxr import Usd


class VariantManagerState(QtCore.QObject):
    """
    Single source of truth for shared application state.
    Components subscribe to signals to react to state changes.
    """
    _instance = None

    # Signals emitted when state changes
    lop_node_changed = QtCore.Signal(object)
    stage_changed = QtCore.Signal(object)
    prim_path_changed = QtCore.Signal(str)
    variant_set_changed = QtCore.Signal(str)

    def __new__(cls):
        # Implements singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialization guard for preventing re-init of singleton
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True

        # Init state variables
        # The currently selected LOP node in the Houdini network
        self._lop_node: Optional[hou.LopNode] = None

        # The USD stage from the current LOP node
        self._stage: Optional[Usd.Stage] = None

        # Path to the currently selected prim (e.g., "/Kitchen/Table")
        self._prim_path: str = ""

        # Name of the currently selected variant set (e.g., "modelVariant")
        self._variant_set: str = ""

    # ─────────────────────────────────────────────────────────────────────────
    # LOP Node
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def lop_node(self):
        """Current LOP node (hou.LopNode or None)."""
        return self._lop_node

    @lop_node.setter # Should always emit signals on change
    def lop_node(self, value):
        if self._lop_node != value:
            self._lop_node = value
            self.lop_node_changed.emit(value)

    # ─────────────────────────────────────────────────────────────────────────
    # USD Stage
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def stage(self):
        """Current USD stage (Usd.Stage or None)."""
        return self._stage

    @stage.setter # Should always emit signals on update, even if value is same
    def stage(self, value):
        self.stage_changed.emit(value)

    # ─────────────────────────────────────────────────────────────────────────
    # Prim Path
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def prim_path(self):
        """Current USD prim path string."""
        return self._prim_path

    @prim_path.setter # Should always emit signals on change, even if value is same
    def prim_path(self, value):
        self.prim_path_changed.emit(value)

    # ─────────────────────────────────────────────────────────────────────────
    # Variant Set
    # ─────────────────────────────────────────────────────────────────────────
    @property
    def variant_set(self):
        """Current variant set name."""
        return self._variant_set

    @variant_set.setter # Should always emit signals on change, even if value is same
    def variant_set(self, value):
        self.variant_set_changed.emit(value)

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience Methods
    # ─────────────────────────────────────────────────────────────────────────
    def clear(self):
        """Reset all state to defaults."""
        self.lop_node = None
        self.stage = None
        self.prim_path = ""
        self.variant_set = ""

    def get_prim(self):
        """
        Get the current prim object from stage and prim_path.

        Returns:
            Usd.Prim or None
        """
        if self._stage and self._prim_path:
            try:
                return self._stage.GetPrimAtPath(self._prim_path)
            except Exception:
                return None
        return None


def get_state():
    """Convenience function to get the singleton state instance."""
    return VariantManagerState()
