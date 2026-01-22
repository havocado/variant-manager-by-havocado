"""
Variant Manager by havocado - USD Variant Inspector Panel for Houdini
Designed to match Houdini's parameter pane and Scene Graph Tree conventions
"""
from PySide6 import QtWidgets, QtCore, QtGui

# Houdini imports - gracefully handle when running outside Houdini
try:
    import hou
    HOU_AVAILABLE = True
except ImportError:
    hou = None
    HOU_AVAILABLE = False

from inspector_tab import InspectorTab
from comparison_tab import ComparisonTab
from analysis_tab import AnalysisTab


# ═══════════════════════════════════════════════════════════════════════════════
# LOP NODE SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class LOPNodeSelector(QtCore.QObject):
    """
    Manages LOP node discovery and stage retrieval for the Variant Manager.
    Emits signals when the selected node or stage changes.
    """
    
    # Signals
    nodeChanged = QtCore.Signal(str)           # Emits node path when selection changes
    stageChanged = QtCore.Signal(object)       # Emits Usd.Stage (or None) when stage changes
    nodesUpdated = QtCore.Signal(list)         # Emits list of available node paths
    errorOccurred = QtCore.Signal(str)         # Emits error message
    
    def __init__(self, parent=None):
        super(LOPNodeSelector, self).__init__(parent)
        self._current_node_path = None
        self._current_stage = None
        self._available_nodes = []
        self._auto_refresh_enabled = False
        self._event_callback_id = None
    
    @property
    def current_node_path(self):
        """Returns the currently selected node path."""
        return self._current_node_path
    
    @property
    def current_stage(self):
        """Returns the USD stage from the current node."""
        return self._current_stage
    
    @property
    def available_nodes(self):
        """Returns list of available LOP node paths."""
        return self._available_nodes
    
    def refresh_node_list(self):
        """Discover all LOP nodes in the scene that have valid stages."""
        if not HOU_AVAILABLE:
            # Return placeholder data for development/testing
            self._available_nodes = ["/stage/variant", "/stage/render", "/stage/output"]
            self.nodesUpdated.emit(self._available_nodes)
            return self._available_nodes
        
        nodes = []
        try:
            # Find all LOP networks
            for node in hou.node("/").allSubChildren():
                if node.type().category().name() == "Lop":
                    # Check if this node can provide a stage
                    try:
                        stage = node.stage()
                        if stage is not None:
                            nodes.append(node.path())
                    except Exception:
                        # Node exists but can't provide stage (may need cooking)
                        nodes.append(node.path())
        except Exception as e:
            self.errorOccurred.emit(f"Error scanning nodes: {str(e)}")
        
        self._available_nodes = sorted(nodes)
        self.nodesUpdated.emit(self._available_nodes)
        return self._available_nodes
    
    def select_node(self, node_path):
        """
        Select a LOP node by path and retrieve its stage.
        
        Args:
            node_path: Full path to the LOP node (e.g., "/stage/variant")
        
        Returns:
            The USD stage if successful, None otherwise
        """
        if not node_path:
            self._current_node_path = None
            self._current_stage = None
            self.nodeChanged.emit("")
            self.stageChanged.emit(None)
            return None
        
        self._current_node_path = node_path
        self.nodeChanged.emit(node_path)
        
        # Get the stage
        stage = self._get_stage_from_node(node_path)
        self._current_stage = stage
        self.stageChanged.emit(stage)
        
        return stage
    
    def _get_stage_from_node(self, node_path):
        """Retrieve the USD stage from a LOP node."""
        if not HOU_AVAILABLE:
            # Return None for development - tabs should handle gracefully
            return None
        
        try:
            node = hou.node(node_path)
            if node is None:
                self.errorOccurred.emit(f"Node not found: {node_path}")
                return None
            
            # Check if it's a LOP node
            if node.type().category().name() != "Lop":
                self.errorOccurred.emit(f"Not a LOP node: {node_path}")
                return None
            
            # Get the stage - this may trigger a cook
            stage = node.stage()
            if stage is None:
                self.errorOccurred.emit(f"No stage available from: {node_path}")
            
            return stage
            
        except Exception as e:
            self.errorOccurred.emit(f"Error getting stage: {str(e)}")
            return None
    
    def refresh_current_stage(self):
        """Re-fetch the stage from the currently selected node."""
        if self._current_node_path:
            return self.select_node(self._current_node_path)
        return None
    
    def select_from_network_selection(self):
        """
        Auto-select based on current network editor selection.
        Useful for syncing with user's node selection in Houdini.
        """
        if not HOU_AVAILABLE:
            return None
        
        try:
            selected = hou.selectedNodes()
            for node in selected:
                if node.type().category().name() == "Lop":
                    return self.select_node(node.path())
        except Exception as e:
            self.errorOccurred.emit(f"Error reading selection: {str(e)}")
        
        return None
    
    def enable_auto_refresh(self, enabled=True):
        """
        Enable/disable automatic refresh when scene changes.
        Uses Houdini's event loop callback.
        """
        self._auto_refresh_enabled = enabled
        # Note: Full implementation would hook into hou.ui.addEventLoopCallback()
        # or use node change callbacks. Simplified for initial implementation.
    
    def jump_to_node(self):
        """Navigate to the current node in the network editor."""
        if not HOU_AVAILABLE or not self._current_node_path:
            return
        
        try:
            node = hou.node(self._current_node_path)
            if node:
                # Find a network editor pane and navigate to the node
                for pane in hou.ui.paneTabs():
                    if pane.type() == hou.paneTabType.NetworkEditor:
                        pane.setCurrentNode(node)
                        pane.homeToSelection()
                        break
        except Exception as e:
            self.errorOccurred.emit(f"Error jumping to node: {str(e)}")


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
        self.lop_selector = LOPNodeSelector(self)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ─────────────────────────────────────────────────────────────────────
        # TAB BAR
        # ─────────────────────────────────────────────────────────────────────
        self.tab_widget = QtWidgets.QTabWidget()
        
        # ─────────────────────────────────────────────────────────────────────
        # SHELF TOOLBAR
        # ─────────────────────────────────────────────────────────────────────
        shelf_toolbar = QtWidgets.QToolBar()
        shelf_toolbar.setMovable(False)
        shelf_toolbar.setIconSize(QtCore.QSize(20, 20))
        
        # Left-aligned tools
        # LOP path label and combobox
        lop_label = QtWidgets.QLabel("Select LOP: ")
        lop_label.setMouseTracking(True)
        lop_label.setToolTip("Choose a LOP node to inspect its USD stage.\n\n"
                             "LOP (Lighting Operator) nodes build and modify USD stages.\n"
                             "Select a node downstream in your network to see the\n"
                             "cumulative result of all upstream operations.")
        shelf_toolbar.addWidget(lop_label)
        
        self.lop_path_combo = QtWidgets.QComboBox()
        self.lop_path_combo.setMinimumWidth(140)
        self.lop_path_combo.setEditable(True)  # Allow manual path entry
        self.lop_path_combo.lineEdit().setPlaceholderText("Select LOP node...")
        self.lop_path_combo.currentTextChanged.connect(self._on_lop_combo_changed)
        shelf_toolbar.addWidget(self.lop_path_combo)
        
        shelf_toolbar.addSeparator()
        
        # Filter button
        filter_btn = QtWidgets.QToolButton()
        filter_btn.setText("🔍")
        filter_btn.setToolTip("Filter variants")
        shelf_toolbar.addWidget(filter_btn)
        
        # Refresh button
        self.refresh_btn = QtWidgets.QToolButton()
        self.refresh_btn.setText("⟳")
        self.refresh_btn.setToolTip("Refresh node list and stage")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        shelf_toolbar.addWidget(self.refresh_btn)
        
        # Multi-select toggle
        multi_btn = QtWidgets.QToolButton()
        multi_btn.setText("⚌")
        multi_btn.setToolTip("Toggle multi-select mode")
        multi_btn.setCheckable(True)
        shelf_toolbar.addWidget(multi_btn)
        
        # Expand/collapse all
        expand_btn = QtWidgets.QToolButton()
        expand_btn.setText("⊞")
        expand_btn.setToolTip("Expand/collapse all folders")
        shelf_toolbar.addWidget(expand_btn)
        
        # Spacer
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        shelf_toolbar.addWidget(spacer)
        
        # Right-aligned tools
        # Copy paths
        copy_btn = QtWidgets.QToolButton()
        copy_btn.setText("📋")
        copy_btn.setToolTip("Copy prim paths")
        shelf_toolbar.addWidget(copy_btn)
        
        # Export report
        export_btn = QtWidgets.QToolButton()
        export_btn.setText("📊")
        export_btn.setToolTip("Export report")
        shelf_toolbar.addWidget(export_btn)
        
        # Settings
        settings_btn = QtWidgets.QToolButton()
        settings_btn.setText("⚙️")
        settings_btn.setToolTip("Panel settings")
        settings_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        settings_menu = QtWidgets.QMenu()
        settings_menu.addAction("Show Hidden Prims")
        settings_menu.addAction("Auto-refresh")
        settings_menu.addSeparator()
        settings_menu.addAction("Preferences...")
        settings_btn.setMenu(settings_menu)
        shelf_toolbar.addWidget(settings_btn)
        
        main_layout.addWidget(shelf_toolbar)
        
        # ─────────────────────────────────────────────────────────────────────
        # TABS
        # ─────────────────────────────────────────────────────────────────────
        # Inspector Tab
        self.inspector_tab = InspectorTab()
        self.inspector_tab.set_source_lop_node_callback(self._get_current_lop_node)
        self.inspector_tab.nodeCreated.connect(self._on_node_created)
        self.tab_widget.addTab(self.inspector_tab, "⚙️ Inspector")

        # Comparison Tab
        self.comparison_tab = ComparisonTab()
        self.tab_widget.addTab(self.comparison_tab, "Comparison")

        # Initialize comparison tab with current LOP node if inspector tab has one
        if hasattr(self.inspector_tab, '_lop_node') and self.inspector_tab._lop_node:
            self.comparison_tab.set_lop_node(self.inspector_tab._lop_node)
            if hasattr(self.inspector_tab, '_stage') and self.inspector_tab._stage:
                self.comparison_tab.set_stage(self.inspector_tab._stage)
        
        # Analysis Tab
        self.analysis_tab = AnalysisTab()
        self.tab_widget.addTab(self.analysis_tab, "Analysis")
        
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
        
        # Separator
        sep2 = QtWidgets.QLabel("│")
        status_layout.addWidget(sep2)
        
        # Warning count
        self.warning_btn = QtWidgets.QPushButton("⚠️ 0")
        self.warning_btn.setFlat(True)
        self.warning_btn.setToolTip("Filter to warnings")
        status_layout.addWidget(self.warning_btn)
        
        # Separator
        sep3 = QtWidgets.QLabel("│")
        status_layout.addWidget(sep3)
        
        # Timestamp
        self.time_label = QtWidgets.QLabel("⏱️ --:--:--")
        self.time_label.setToolTip("Last refresh timestamp")
        status_layout.addWidget(self.time_label)
        
        status_layout.addStretch()
        
        main_layout.addWidget(status_bar)
        
        # ─────────────────────────────────────────────────────────────────────
        # CONNECT SIGNALS
        # ─────────────────────────────────────────────────────────────────────
        self.lop_selector.nodeChanged.connect(self._on_node_changed)
        self.lop_selector.stageChanged.connect(self._on_stage_changed)
        self.lop_selector.nodesUpdated.connect(self._on_nodes_updated)
        self.lop_selector.errorOccurred.connect(self._on_error)

        # Connect inspector tab signals
        self.inspector_tab.primPathChanged.connect(self._on_prim_path_changed)

        # Initial population
        self._refresh_node_list()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOP SELECTOR SLOTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _refresh_node_list(self):
        """Refresh the list of available LOP nodes."""
        self.lop_selector.refresh_node_list()
    
    def _on_lop_combo_changed(self, text):
        """Handle combo box selection change."""
        if text and text != self.lop_selector.current_node_path:
            self.lop_selector.select_node(text)
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        import datetime
        self._refresh_node_list()
        self.lop_selector.refresh_current_stage()
        self.time_label.setText("⏱️ " + datetime.datetime.now().strftime("%H:%M:%S"))
    
    def _on_node_changed(self, node_path):
        """Handle node selection change."""
        # Update status bar
        if node_path:
            self.status_lop_path_btn.setText(node_path)
        else:
            self.status_lop_path_btn.setText("No node selected")
        
        # Update combo if needed (avoid recursive signal)
        if self.lop_path_combo.currentText() != node_path:
            self.lop_path_combo.blockSignals(True)
            self.lop_path_combo.setCurrentText(node_path or "")
            self.lop_path_combo.blockSignals(False)
    
    def _on_stage_changed(self, stage):
        """Handle stage change - notify all tabs."""
        import datetime
        self.time_label.setText("⏱️ " + datetime.datetime.now().strftime("%H:%M:%S"))

        # Update prim count in status bar
        if stage:
            try:
                prim_count = len(list(stage.Traverse()))
                self.selection_label.setText(f"{prim_count} prims")
            except Exception:
                self.selection_label.setText("? prims")
        else:
            self.selection_label.setText("0 prims")

        # Get the current LOP node for thumbnail generation
        lop_node = self._get_current_lop_node()
        print(f"[VariantManager] _on_stage_changed: stage={stage}, lop_node={lop_node}")

        # Notify tabs - they should implement set_stage() method
        if hasattr(self.inspector_tab, 'set_stage'):
            self.inspector_tab.set_stage(stage)
        if hasattr(self.comparison_tab, 'set_stage'):
            self.comparison_tab.set_stage(stage)
        if hasattr(self.comparison_tab, 'set_lop_node'):
            print(f"[VariantManager] Calling comparison_tab.set_lop_node with: {lop_node}")
            self.comparison_tab.set_lop_node(lop_node)
        else:
            print(f"[VariantManager] comparison_tab does not have set_lop_node method")
        if hasattr(self.analysis_tab, 'set_stage'):
            self.analysis_tab.set_stage(stage)
    
    def _on_nodes_updated(self, node_paths):
        """Handle node list update."""
        # Update combo box
        current = self.lop_path_combo.currentText()
        self.lop_path_combo.blockSignals(True)
        self.lop_path_combo.clear()
        self.lop_path_combo.addItems(node_paths)
        if current in node_paths:
            self.lop_path_combo.setCurrentText(current)
        self.lop_path_combo.blockSignals(False)
    
    def _on_error(self, message):
        """Handle error from LOP selector."""
        # Could show in status bar or as tooltip
        self.status_lop_path_btn.setToolTip(f"Error: {message}")
    
    def _on_jump_to_node(self):
        """Jump to the current node in the network editor."""
        self.lop_selector.jump_to_node()
    
    def _get_current_lop_node(self):
        """
        Get the currently selected LOP node object.
        Used as a callback for child widgets that need to create nodes.
        
        Returns:
            hou.LopNode or None
        """
        if not HOU_AVAILABLE:
            return None
        
        node_path = self.lop_selector.current_node_path
        if not node_path:
            return None
        
        try:
            return hou.node(node_path)
        except Exception:
            return None
    
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
        self.lop_selector.select_node(node_path)

    def _on_prim_path_changed(self, prim_path):
        """
        Handle when the selected prim path changes in the Inspector tab.
        Forward the path to the Comparison tab.

        Args:
            prim_path: The USD prim path string, or empty string for no selection
        """
        # Ensure comparison tab has the stage before setting prim path
        # This handles the case where the inspector tab was initialized with a stage
        # but _on_stage_changed was never called (initialization order issue)
        if hasattr(self.comparison_tab, '_stage') and self.comparison_tab._stage is None:
            if hasattr(self.inspector_tab, '_stage') and self.inspector_tab._stage is not None:
                self.comparison_tab.set_stage(self.inspector_tab._stage)

        if hasattr(self.comparison_tab, 'set_prim_path'):
            self.comparison_tab.set_prim_path(prim_path)


def createInterface():
    """Required function for Houdini Python Panel"""
    return VariantManagerPanel()