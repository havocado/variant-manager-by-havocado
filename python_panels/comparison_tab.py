"""
Comparison Tab for Variant Manager by havocado
"""
from PySide6 import QtWidgets, QtCore, QtGui

from widgets import ComparisonPanelWidget
from node_utils import create_set_variant_node, configure_set_variant_node, jump_to_node

try:
    from thumbnail import ThumbnailManager
    THUMBNAIL_AVAILABLE = True
except ImportError:
    ThumbnailManager = None
    THUMBNAIL_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON TAB
# ═══════════════════════════════════════════════════════════════════════════════

class ComparisonTab(QtWidgets.QWidget):
    """Comparison tab with viewport gallery"""

    # Signal emitted when a new node is created, with the new node's path
    nodeCreated = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(ComparisonTab, self).__init__(parent)

        self._panels = []  # Store panel widgets for reordering
        self._current_view_mode = "Side-by-Side"
        self._current_prim = None
        self._current_variant_set = None  # Track current variant set name
        self._thumbnail_manager = None  # Will be initialized when LOP node is set

        # Callback to get LOP node from main panel (for creating new nodes and thumbnails)
        self._get_source_lop_node_callback = None

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

        # Separator
        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.VLine)
        controls_layout.addWidget(sep2)

        # Create Thumbnails button
        self.create_thumbnails_btn = QtWidgets.QPushButton("Create Thumbnails from Current Viewport")
        self.create_thumbnails_btn.setEnabled(False)
        self.create_thumbnails_btn.setToolTip("Generate thumbnails for all variants using the current viewport camera")
        self.create_thumbnails_btn.clicked.connect(self._on_create_thumbnails_clicked)
        controls_layout.addWidget(self.create_thumbnails_btn)
        
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

    def set_stage(self, stage, lop_node=None):
        """
        Set the USD stage for comparison view.
        Called by the main panel when the stage changes.

        Args:
            stage: A Usd.Stage object or None
            lop_node: A hou.LopNode object or None (for thumbnail generation)
        """
        self._refresh_from_stage(stage)

        # Update thumbnail manager if we have a LOP node
        if lop_node:
            self._update_thumbnail_manager(lop_node)

    def _update_thumbnail_manager(self, lop_node):
        """
        Update or initialize the thumbnail manager with a new LOP node.

        Args:
            lop_node: A hou.LopNode object or None
        """
        # Clean up existing thumbnail manager
        if self._thumbnail_manager:
            try:
                self._thumbnail_manager.cleanup()
            except:
                pass
            self._thumbnail_manager = None

        # Initialize new thumbnail manager if we have a LOP node
        if lop_node and THUMBNAIL_AVAILABLE:
            try:
                self._thumbnail_manager = ThumbnailManager(lop_node, parent=self)
                self._thumbnail_manager.thumbnail_ready.connect(self._on_thumbnail_ready)
                self._thumbnail_manager.generation_failed.connect(self._on_thumbnail_failed)
            except Exception as e:
                print(f"Failed to initialize thumbnail manager: {e}")
                import traceback
                traceback.print_exc()
                self._thumbnail_manager = None

    def set_get_source_lop_node_callback(self, callback):
        """
        Set the callback function to get the source LOP node from the main panel.

        Args:
            callback: A callable that returns a hou.LopNode or None
        """
        self._get_source_lop_node_callback = callback

    def _refresh_from_stage(self, stage):
        """
        Refresh the comparison panels from the given stage.

        Args:
            stage: A Usd.Stage object or None (passed from parent)
        """
        if stage is None:
            self._current_prim = None
            return

        # If we have a current prim path, refresh it from the new stage
        if self._current_prim is not None:
            try:
                prim_path = str(self._current_prim.GetPath())
                self._current_prim = stage.GetPrimAtPath(prim_path)
            except:
                self._current_prim = None

    def set_prim_path(self, prim_path, stage=None):
        """
        Set the prim path for the comparison tab.
        Called when the user selects a prim in the Inspector tab.

        Args:
            prim_path: The USD prim path string, or empty string for no selection
            stage: Optional Usd.Stage object. If provided, use this stage to get the prim.
        """
        if prim_path and stage is not None:
            # Get the prim and populate variant sets
            try:
                self._current_prim = stage.GetPrimAtPath(prim_path)
                self._populate_variant_sets()
            except Exception as e:
                print(f"Error getting prim at path {prim_path}: {e}")
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

        # Store current variant set name
        self._current_variant_set = variant_set_name

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

        # Get the prim path for context
        prim_path = str(self._current_prim.GetPath()) if self._current_prim else ""

        # Create a panel for each variant
        for variant_name in variant_names:
            panel = ComparisonPanelWidget(variant_name)
            panel.set_loading()  # Show loading state initially

            # Set variant context for the switch button
            if prim_path and self._current_variant_set:
                panel.set_variant_context(prim_path, self._current_variant_set, variant_name)

            # Connect the switch button to the handler
            panel.switch_btn.clicked.connect(self._on_switch_variant_clicked)

            self._panels.append(panel)

        # Re-layout panels according to current view mode
        self._reorganize_panels()

        # Enable the create thumbnails button if we have panels and a thumbnail manager
        self.create_thumbnails_btn.setEnabled(
            len(self._panels) > 0 and self._thumbnail_manager is not None
        )

    def _clear_panels(self):
        """Remove all comparison panels."""
        # Remove panels from layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear panels list
        self._panels = []

        # Disable the create thumbnails button
        self.create_thumbnails_btn.setEnabled(False)

    def _on_create_thumbnails_clicked(self):
        """Handle the 'Create Thumbnails' button click."""
        self._request_all_thumbnails()

    def _request_all_thumbnails(self):
        """Request thumbnails for all panels."""
        if not self._thumbnail_manager or not self._current_prim or not self._current_variant_set:
            return

        prim_path = str(self._current_prim.GetPath())

        # Get variant set to retrieve variant names
        variant_sets = self._current_prim.GetVariantSets()
        variant_set = variant_sets.GetVariantSet(self._current_variant_set)

        if not variant_set:
            return

        variant_names = variant_set.GetVariantNames()

        # Request thumbnails for all panels
        for index, variant_name in enumerate(variant_names):
            self._thumbnail_manager.request_thumbnail(
                index,
                prim_path,
                self._current_variant_set,
                variant_name
            )

    def _on_thumbnail_ready(self, index, pixmap):
        """
        Callback when a thumbnail is ready.

        Args:
            index: Panel index
            pixmap: QPixmap of the thumbnail
        """
        if index < len(self._panels):
            self._panels[index].set_thumbnail(pixmap)

    def _on_thumbnail_failed(self, index, error_message):
        """
        Callback when thumbnail generation fails.

        Args:
            index: Panel index
            error_message: Error description
        """
        if index < len(self._panels):
            self._panels[index].set_failed()
            print(f"Thumbnail generation failed for panel {index}: {error_message}")

    def _get_source_lop_node(self):
        """
        Get the source LOP node from the main panel's selector.

        Returns:
            hou.LopNode or None
        """
        if self._get_source_lop_node_callback:
            return self._get_source_lop_node_callback()
        return None

    def _on_switch_variant_clicked(self):
        """Handle Switch button click - create a Set Variant node."""
        sender = self.sender()
        if sender is None:
            return

        # Get stored context from button properties
        prim_path = sender.property("prim_path")
        variant_set = sender.property("variant_set")
        variant_choice = sender.property("variant_choice")

        if not all([prim_path, variant_set, variant_choice]):
            print("Missing variant context on Switch button")
            return

        # Get the source LOP node from the main panel's selector
        source_node = self._get_source_lop_node()
        if source_node is None:
            print("No LOP node selected in the panel")
            return

        try:
            # Create the Set Variant node after the source LOP node
            new_node = create_set_variant_node(source_node)

            if new_node:
                # Configure node parameters: primitives, variant set, variant name
                configure_set_variant_node(new_node, prim_path, variant_set, variant_choice)

                # Jump to the new node in the network editor and select it
                jump_to_node(new_node)

                # Notify the main panel to update its LOP selector
                self.nodeCreated.emit(new_node.path())

        except Exception as e:
            print(f"Failed to create Set Variant node: {e}")
