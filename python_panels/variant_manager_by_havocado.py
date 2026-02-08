"""
Variant Manager by havocado - USD Variant Inspector Panel for Houdini
Designed to match Houdini's parameter pane and Scene Graph Tree conventions
"""
from PySide6 import QtWidgets

from inspector_tab import InspectorTab
from comparison_tab import ComparisonTab
from state import get_state
from lop_utils import LOPNodeCoordinator
from widgets import LOPPathComboBox
from node_utils import is_node_valid


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PANEL WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class VariantManagerPanel(QtWidgets.QWidget):
    """USD Variant Inspector Panel - Houdini Native Style"""
    
    def __init__(self, parent=None):
        super(VariantManagerPanel, self).__init__(parent)
        
        # Set window properties
        self.setWindowTitle("USD Variant Inspector")
        self.setMinimumSize(200, 150)  # Allow smaller resize
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # ─────────────────────────────────────────────────────────────────────
        # LOP NODE SELECTOR (Core Logic)
        # ─────────────────────────────────────────────────────────────────────
        self.lop_selector = LOPNodeCoordinator(self)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ─────────────────────────────────────────────────────────────────────
        # TAB BAR
        # ─────────────────────────────────────────────────────────────────────
        self.tab_widget = QtWidgets.QTabWidget()
        
        # ─────────────────────────────────────────────────────────────────────
        # LOP SELECTOR BAR
        # ─────────────────────────────────────────────────────────────────────
        lop_bar = QtWidgets.QWidget()
        lop_bar_layout = QtWidgets.QHBoxLayout(lop_bar)
        lop_bar_layout.setContentsMargins(4, 4, 4, 4)
        lop_bar_layout.setSpacing(6)

        lop_label = QtWidgets.QLabel("Select LOP:")
        lop_label.setToolTip("Choose a LOP node to inspect its USD stage.\n\n"
                             "LOP (Lighting Operator) nodes build and modify USD stages.\n"
                             "Select a node downstream in your network to see the\n"
                             "cumulative result of all upstream operations.")
        lop_bar_layout.addWidget(lop_label)

        self.lop_path_combo = LOPPathComboBox()
        self.lop_path_combo.currentTextChanged.connect(self._on_lop_combo_changed)
        self.lop_path_combo.aboutToShowPopup.connect(self._refresh_node_list)
        lop_bar_layout.addWidget(self.lop_path_combo)

        main_layout.addWidget(lop_bar)
        
        # ─────────────────────────────────────────────────────────────────────
        # TABS
        # ─────────────────────────────────────────────────────────────────────
        # Inspector Tab
        self.inspector_tab = InspectorTab()
        self.inspector_tab.nodeCreated.connect(self._on_node_created)
        self.tab_widget.addTab(self.inspector_tab, "⚙️ Inspector")

        # Comparison Tab
        self.comparison_tab = ComparisonTab()
        self.comparison_tab.nodeCreated.connect(self._on_node_created)
        self.tab_widget.addTab(self.comparison_tab, "Comparison")

        main_layout.addWidget(self.tab_widget)
        
        # ─────────────────────────────────────────────────────────────────────
        # STATUS BAR
        # ─────────────────────────────────────────────────────────────────────
        status_bar = QtWidgets.QFrame()
        status_bar.setFixedHeight(28)
        
        status_layout = QtWidgets.QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(0)
        
        # LOP node path
        lop_icon = QtWidgets.QLabel("🔗")
        status_layout.addWidget(lop_icon)
        
        self.status_lop_path_btn = QtWidgets.QPushButton("No node selected")
        self.status_lop_path_btn.setFlat(True)
        self.status_lop_path_btn.setToolTip("Jump to network")
        self.status_lop_path_btn.clicked.connect(self._on_jump_to_node)
        status_layout.addWidget(self.status_lop_path_btn)
        
        # Separator
        sep1 = QtWidgets.QLabel("│")
        status_layout.addWidget(sep1)
        
        # Selection count
        self.selection_label = QtWidgets.QLabel("0 prims")
        status_layout.addWidget(self.selection_label)
        
        status_layout.addStretch()
        
        main_layout.addWidget(status_bar)
        
        # ─────────────────────────────────────────────────────────────────────
        # CONNECT SIGNALS
        # ─────────────────────────────────────────────────────────────────────
        # State signals for UI updates
        state = get_state()
        state.lop_node_changed.connect(self._on_lop_node_changed)
        state.stage_changed.connect(self._on_stage_changed)

        # LOP selector signals for combo box and errors
        self.lop_selector.nodesUpdated.connect(self._on_nodes_updated)
        self.lop_selector.errorOccurred.connect(self._on_error)

        # Initial population
        self._refresh_node_list()

        # Discover and select initial LOP node
        self.lop_selector.discover_initial_node()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOP SELECTOR SLOTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _refresh_node_list(self):
        """Refresh the list of available LOP nodes."""
        self.lop_selector.refresh_node_list()

    def _on_lop_combo_changed(self, text):
        """Callback for signal currentTextChanged (lop_path_combo)."""
        if text:
            self.lop_selector.select_lop_node_states(text)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self._refresh_node_list()
        self.lop_selector.refresh_current_stage()

    def _on_lop_node_changed(self, lop_node):
        """Callback for signal lop_node_changed."""
        node_path = lop_node.path() if is_node_valid(lop_node) else ""

        # Update status bar
        if node_path:
            self.status_lop_path_btn.setText(node_path)
        else:
            self.status_lop_path_btn.setText("No node selected")

        # Update combo if needed (avoid recursive signal)
        if self.lop_path_combo.currentText() != node_path:
            self.lop_path_combo.blockSignals(True)
            self.lop_path_combo.setCurrentText(node_path)
            self.lop_path_combo.blockSignals(False)

    def _on_stage_changed(self, stage):
        """Callback for signal stage_changed."""

        # Update prim count in status bar
        if stage:
            try:
                prim_count = len(list(stage.Traverse()))
                self.selection_label.setText(f"{prim_count} prims")
            except Exception:
                self.selection_label.setText("? prims")
        else:
            self.selection_label.setText("0 prims")
    
    def _on_nodes_updated(self, node_paths):
        """Handle node list update."""
        old_text = self.lop_path_combo.currentText()

        self.lop_path_combo.blockSignals(True)
        self.lop_path_combo.clear()
        self.lop_path_combo.addItems(node_paths)
        if old_text in node_paths:
            self.lop_path_combo.setCurrentText(old_text)
        self.lop_path_combo.blockSignals(False)

        # If selection changed due to population, manually trigger handler
        new_text = self.lop_path_combo.currentText()
        if new_text != old_text:
            self._on_lop_combo_changed(new_text)
    
    def _on_error(self, message):
        """Handle error from LOP selector."""
        # Could show in status bar or as tooltip
        self.status_lop_path_btn.setToolTip(f"Error: {message}")
    
    def _on_jump_to_node(self):
        """Jump to the current node in the network editor."""
        self.lop_selector.jump_to_node()
    
    def _on_node_created(self, node_path):
        """
        Handle when a new node is created by a child widget.
        Updates the LOP selector to point to the new node.

        Args:
            node_path: The path of the newly created node
        """
        if not node_path:
            return

        # Refresh node list to include the new node
        self._refresh_node_list()

        # Select the new node (this will trigger _on_stage_changed which updates comparison tab)
        self.lop_selector.select_lop_node_states(node_path)


def createInterface():
    """Required function for Houdini Python Panel"""
    return VariantManagerPanel()