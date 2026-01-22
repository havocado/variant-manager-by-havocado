"""
Comparison Tab for Variant Manager by havocado
"""
from PySide6 import QtWidgets, QtCore, QtGui

from widgets import ComparisonPanelWidget


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON TAB
# ═══════════════════════════════════════════════════════════════════════════════

class ComparisonTab(QtWidgets.QWidget):
    """Comparison tab with viewport gallery"""

    def __init__(self, parent=None):
        super(ComparisonTab, self).__init__(parent)

        self._panels = []  # Store panel widgets for reordering
        self._current_view_mode = "Side-by-Side"
        self._stage = None
        self._current_prim = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # ─────────────────────────────────────────────────────────────────────
        # Controls Bar
        # ─────────────────────────────────────────────────────────────────────
        controls_bar = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls_bar)
        controls_layout.setContentsMargins(8, 4, 8, 4)
        controls_layout.setSpacing(12)

        # View mode
        view_label = QtWidgets.QLabel("View:")
        controls_layout.addWidget(view_label)

        self.view_combo = QtWidgets.QComboBox()
        self.view_combo.addItems(["Side-by-Side", "2x2 Grid", "3x3 Grid", "Vertical Stack"])
        self.view_combo.currentTextChanged.connect(self._on_view_mode_changed)
        controls_layout.addWidget(self.view_combo)

        # Separator
        sep1 = QtWidgets.QFrame()
        sep1.setFrameShape(QtWidgets.QFrame.VLine)
        controls_layout.addWidget(sep1)

        # Variant Set selector
        variant_set_label = QtWidgets.QLabel("Variant Set:")
        controls_layout.addWidget(variant_set_label)

        self.variant_set_combo = QtWidgets.QComboBox()
        self.variant_set_combo.setMinimumWidth(120)
        self.variant_set_combo.addItem("(No variant sets)")
        self.variant_set_combo.setEnabled(False)
        self.variant_set_combo.setToolTip("Select a variant set from the current prim")
        self.variant_set_combo.currentTextChanged.connect(self._on_variant_set_changed)
        controls_layout.addWidget(self.variant_set_combo)

        controls_layout.addStretch()
        
        layout.addWidget(controls_bar)

        # ─────────────────────────────────────────────────────────────────────
        # Comparison Panels Container (Scroll Area)
        # ─────────────────────────────────────────────────────────────────────
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QHBoxLayout(self.grid_widget)  # Default to horizontal
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setSpacing(8)

        # Initially empty - panels will be created when a variant set is selected
        # for panel in self._panels:
        #     self.grid_layout.addWidget(panel)

        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)

    def _on_view_mode_changed(self, mode):
        """Handle view mode change and reorganize panels"""
        self._current_view_mode = mode
        self._reorganize_panels()

    def _reorganize_panels(self):
        """Reorganize panels based on current view mode"""
        # Remove all panels from current layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Delete the old layout
        QtWidgets.QWidget().setLayout(self.grid_layout)

        # Create new layout based on view mode
        if self._current_view_mode == "Side-by-Side":
            self.grid_layout = QtWidgets.QHBoxLayout(self.grid_widget)
            self.grid_layout.setContentsMargins(4, 4, 4, 4)
            self.grid_layout.setSpacing(8)

            # Add all panels horizontally
            for panel in self._panels:
                self.grid_layout.addWidget(panel)

        elif self._current_view_mode == "Vertical Stack":
            self.grid_layout = QtWidgets.QVBoxLayout(self.grid_widget)
            self.grid_layout.setContentsMargins(4, 4, 4, 4)
            self.grid_layout.setSpacing(8)

            # Add all panels vertically
            for panel in self._panels:
                self.grid_layout.addWidget(panel)

        elif self._current_view_mode == "2x2 Grid":
            self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
            self.grid_layout.setContentsMargins(4, 4, 4, 4)
            self.grid_layout.setSpacing(8)

            # Add panels in 2x2 grid
            for i, panel in enumerate(self._panels):
                row = i // 2
                col = i % 2
                self.grid_layout.addWidget(panel, row, col)

        elif self._current_view_mode == "3x3 Grid":
            self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
            self.grid_layout.setContentsMargins(4, 4, 4, 4)
            self.grid_layout.setSpacing(8)

            # Add panels in 3x3 grid
            for i, panel in enumerate(self._panels):
                row = i // 3
                col = i % 3
                self.grid_layout.addWidget(panel, row, col)

        # Ensure widget updates
        self.grid_widget.setLayout(self.grid_layout)
        self.grid_widget.updateGeometry()

    def set_stage(self, stage):
        """
        Set the USD stage for comparison view.

        Args:
            stage: A Usd.Stage object or None
        """
        self._stage = stage
        self._refresh_from_stage()

    def _refresh_from_stage(self):
        """
        Refresh the comparison panels from the current stage.
        TODO: Implement actual variant comparison logic.
        """
        if not hasattr(self, '_stage') or self._stage is None:
            return

        # TODO: Create comparison panels for selected prims with variants
        pass

    def set_prim_path(self, prim_path):
        """
        Set the prim path for the comparison tab.
        Called when the user selects a prim in the Inspector tab.

        Args:
            prim_path: The USD prim path string, or empty string for no selection
        """
        if prim_path:
            # Get the prim and populate variant sets
            if self._stage is not None:
                try:
                    self._current_prim = self._stage.GetPrimAtPath(prim_path)
                    self._populate_variant_sets()
                except Exception as e:
                    print(f"Error getting prim at path {prim_path}: {e}")
                    self._current_prim = None
                    self._clear_variant_sets()
            else:
                self._current_prim = None
                self._clear_variant_sets()
        else:
            self._current_prim = None
            self._clear_variant_sets()

    def _populate_variant_sets(self):
        """Populate the variant set dropdown with available variant sets from the current prim."""
        self.variant_set_combo.blockSignals(True)
        self.variant_set_combo.clear()

        if self._current_prim and self._current_prim.IsValid():
            variant_sets = self._current_prim.GetVariantSets()
            set_names = list(variant_sets.GetNames())

            if set_names:
                self.variant_set_combo.addItems(set_names)
                self.variant_set_combo.setEnabled(True)
                self.variant_set_combo.blockSignals(False)
                # Trigger loading of the first variant set
                self._on_variant_set_changed(set_names[0])
            else:
                self.variant_set_combo.addItem("(No variant sets)")
                self.variant_set_combo.setEnabled(False)
                self.variant_set_combo.blockSignals(False)
                self._clear_panels()
        else:
            self.variant_set_combo.addItem("(No variant sets)")
            self.variant_set_combo.setEnabled(False)
            self.variant_set_combo.blockSignals(False)
            self._clear_panels()

    def _clear_variant_sets(self):
        """Clear the variant set dropdown."""
        self.variant_set_combo.blockSignals(True)
        self.variant_set_combo.clear()
        self.variant_set_combo.addItem("(No variant sets)")
        self.variant_set_combo.setEnabled(False)
        self.variant_set_combo.blockSignals(False)
        self._clear_panels()

    def _on_variant_set_changed(self, variant_set_name):
        """Handle variant set selection change and rebuild comparison panels."""
        if variant_set_name == "(No variant sets)" or not self._current_prim or not self._current_prim.IsValid():
            self._clear_panels()
            return

        # Get all variants for the selected variant set
        variant_sets = self._current_prim.GetVariantSets()
        variant_set = variant_sets.GetVariantSet(variant_set_name)

        if variant_set:
            variant_names = variant_set.GetVariantNames()
            self._rebuild_panels(variant_names)
        else:
            self._clear_panels()

    def _rebuild_panels(self, variant_names):
        """Rebuild comparison panels for the given variant names."""
        # Clear existing panels
        self._clear_panels()

        # Create a panel for each variant
        for variant_name in variant_names:
            panel = ComparisonPanelWidget(variant_name)
            self._panels.append(panel)

        # Re-layout panels according to current view mode
        self._reorganize_panels()

    def _clear_panels(self):
        """Remove all comparison panels."""
        # Remove panels from layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear panels list
        self._panels = []
