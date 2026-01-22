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
        
        # Sync options
        sync_label = QtWidgets.QLabel("Sync:")
        controls_layout.addWidget(sync_label)
        
        camera_check = QtWidgets.QCheckBox("Camera")
        camera_check.setChecked(True)
        controls_layout.addWidget(camera_check)
        
        frame_check = QtWidgets.QCheckBox("Frame")
        frame_check.setChecked(True)
        controls_layout.addWidget(frame_check)
        
        shading_check = QtWidgets.QCheckBox("Shading")
        controls_layout.addWidget(shading_check)
        
        controls_layout.addStretch()
        
        # Settings
        settings_btn = QtWidgets.QToolButton()
        settings_btn.setText("⚙️")
        settings_btn.setToolTip("Comparison settings")
        controls_layout.addWidget(settings_btn)
        
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

        # Create placeholder panels
        panel_a = ComparisonPanelWidget("/World/Car_A", "sedan")
        panel_a.add_variant_info("model", "sedan")
        panel_a.add_variant_info("shade", "red", has_warning=True)
        panel_a.add_variant_info("wheel", "sport")
        self._panels.append(panel_a)

        panel_b = ComparisonPanelWidget("/World/Car_B", "suv")
        panel_b.add_variant_info("model", "suv")
        panel_b.add_variant_info("shade", "blue")
        panel_b.add_variant_info("wheel", "offroad")
        self._panels.append(panel_b)

        panel_c = ComparisonPanelWidget("/World/Car_C", "sedan")
        panel_c.add_variant_info("model", "sedan")
        panel_c.add_variant_info("shade", "red", has_warning=True)
        panel_c.add_variant_info("wheel", "default")
        self._panels.append(panel_c)

        # Add panels to initial layout
        for panel in self._panels:
            self.grid_layout.addWidget(panel)

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
