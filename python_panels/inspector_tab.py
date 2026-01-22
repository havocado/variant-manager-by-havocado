"""
Inspector Tab for Variant Manager by havocado
"""
from PySide6 import QtWidgets, QtCore, QtGui

try:
    import hou
except ImportError:
    hou = None

from widgets import CollapsibleFolder, VariantSetRow
from node_utils import create_set_variant_node, configure_set_variant_node, jump_to_node


def highlight_prims_in_viewport(prim_paths):
    """
    Highlight prims in the viewport to highlight them, similar to Scene Graph Tree behavior.
    Args:
        prim_paths: A list of USD prim path strings to select.
    Returns:
        True if selection was successful, False otherwise.
    """
    if hou is None:
        return False
    try:
        # Use setCurrentSceneGraphSelection with a list of prim paths (Houdini 19.0+)
        for pane in hou.ui.paneTabs():
            if pane.type() == hou.paneTabType.SceneViewer:
                pwd = pane.pwd()
                if pwd and pwd.childTypeCategory() == hou.lopNodeTypeCategory():
                    pane.setCurrentSceneGraphSelection(prim_paths)
                    return True
        return False
    except Exception as e:
        print(f"Failed to highlight prims in viewport: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR TAB
# ═══════════════════════════════════════════════════════════════════════════════

class InspectorTab(QtWidgets.QWidget):
    """Inspector tab with split pane layout"""

    # Define signal to be emitted when a new node is created, with the new node's path
    # For example: when a "Set Variant" node is created from this tab
    nodeCreated = QtCore.Signal(str)

    # Signal emitted when the selected prim path changes (or selection is cleared)
    primPathChanged = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        super(InspectorTab, self).__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)  # Make handle easier to grab
        
        # ─────────────────────────────────────────────────────────────────────
        # LEFT PANE: Prim Hierarchy
        # ─────────────────────────────────────────────────────────────────────
        left_pane = QtWidgets.QWidget()
        left_pane.setMinimumWidth(150)
        left_pane.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        left_layout = QtWidgets.QVBoxLayout(left_pane)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(4)
        
        # Header with search
        left_header = QtWidgets.QWidget()
        left_header_layout = QtWidgets.QHBoxLayout(left_header)
        left_header_layout.setContentsMargins(0, 0, 0, 0)
        left_header_layout.setSpacing(4)
        
        scene_label = QtWidgets.QLabel("Variant List")
        left_header_layout.addWidget(scene_label)
        
        left_header_layout.addStretch()
        
        # Search field
        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText("🔍 Filter...")
        search_field.setMaximumWidth(120)
        left_header_layout.addWidget(search_field)
        
        left_layout.addWidget(left_header)
        
        # Store search field reference for filtering
        self.search_field = search_field
        self.search_field.textChanged.connect(self._apply_filter)
        
        # Tree widget for hierarchical variant browser
        self.variant_tree = QtWidgets.QTreeWidget()
        self.variant_tree.setHeaderHidden(True)
        self.variant_tree.setAlternatingRowColors(True)
        self.variant_tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.variant_tree.setExpandsOnDoubleClick(True)
        self.variant_tree.setAnimated(True)
        
        # Storage for variant prim data
        self._variant_prims = []
        self._path_to_item = {}  # Map paths to tree items
        self._stage = None
        self._lop_node = None
        self._get_source_lop_node_callback = None  # Callback to get source LOP node from main panel # TODO: restructure
        
        left_layout.addWidget(self.variant_tree)

        splitter.addWidget(left_pane)
        
        # ─────────────────────────────────────────────────────────────────────
        # RIGHT PANE: Variant Details
        # ─────────────────────────────────────────────────────────────────────
        right_pane = QtWidgets.QWidget()
        right_pane.setMinimumWidth(200)
        right_pane.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_layout = QtWidgets.QVBoxLayout(right_pane)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(4)
        
        # Context strip
        context_strip = QtWidgets.QFrame()
        context_layout = QtWidgets.QHBoxLayout(context_strip)
        context_layout.setContentsMargins(8, 4, 8, 4)
        context_layout.setSpacing(8)
        
        # Prim path
        self.path_label = QtWidgets.QLabel("(No selection)")
        context_layout.addWidget(self.path_label)

        # Copy path label
        self.copy_path_label = QtWidgets.QPushButton("Copy")
        self.copy_path_label.setToolTip("Copy path to clipboard")
        self.copy_path_label.setVisible(False)  # Hidden when no selection
        self.copy_path_label.clicked.connect(self._copy_path_to_clipboard)
        context_layout.addWidget(self.copy_path_label)

        context_layout.addStretch()
        
        right_layout.addWidget(context_strip)
        
        # Placeholder label for empty states
        self.placeholder_label = QtWidgets.QLabel()
        self.placeholder_label.setAlignment(QtCore.Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: gray; font-size: 14px; padding: 40px;")
        self.placeholder_label.setWordWrap(True)
        right_layout.addWidget(self.placeholder_label)
        
        # Scroll area for folders
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(4, 4, 4, 4)
        scroll_layout.setSpacing(8)
        
        # ─────────────────────────────────────────────────────────────────────
        # Variant Sets Folder
        # ─────────────────────────────────────────────────────────────────────
        self.variant_sets_folder = CollapsibleFolder("Variant Sets", expanded=True)
        self._variant_set_rows = []  # Store row widgets for cleanup
        
        scroll_layout.addWidget(self.variant_sets_folder)
        
        # ─────────────────────────────────────────────────────────────────────
        # Properties Folder
        # ─────────────────────────────────────────────────────────────────────
        self.properties_folder = CollapsibleFolder("Properties", expanded=True)
        self._property_widgets = []  # Store for cleanup
        
        scroll_layout.addWidget(self.properties_folder)
        
        # ─────────────────────────────────────────────────────────────────────
        # Layer Stack Folder
        # ─────────────────────────────────────────────────────────────────────
        self.layer_folder = CollapsibleFolder("Layer Stack", expanded=True)
        self._layer_widgets = []  # Store for cleanup
        
        scroll_layout.addWidget(self.layer_folder)
        
        # ─────────────────────────────────────────────────────────────────────
        # References & Payloads Folder
        # ─────────────────────────────────────────────────────────────────────
        self.refs_folder = CollapsibleFolder("References & Payloads", expanded=True)
        self._ref_widgets = []  # Store for cleanup
        
        scroll_layout.addWidget(self.refs_folder)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        self.details_scroll = scroll  # Store reference to show/hide
        right_layout.addWidget(scroll)
        
        # Bottom bar with copy button
        bottom_bar = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(4, 4, 4, 4)
        bottom_layout.setSpacing(4)
        
        bottom_layout.addStretch()
        
        copy_btn = QtWidgets.QPushButton("Copy")
        copy_btn.setToolTip("Copy details to clipboard")
        copy_btn.setMaximumWidth(80)
        copy_btn.clicked.connect(self._copy_details_to_clipboard)
        bottom_layout.addWidget(copy_btn)
        
        self.bottom_bar = bottom_bar  # Store reference to show/hide
        right_layout.addWidget(bottom_bar)
        
        splitter.addWidget(right_pane)
        
        # Set initial splitter sizes (30% / 70%)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # Initialize from current LOP node if available (must be after all widgets created)
        self._init_from_lop()
    
    def _init_from_lop(self):
        """Initialize from the current LOP node context"""
        if hou is None:
            return
        
        # Try to get the current LOP node from various sources
        lop_node = self._get_current_lop_node()
        if lop_node:
            self.set_lop_node(lop_node)
    
    def _get_current_lop_node(self):
        """
        Get the current LOP node from Houdini context.
        Tries multiple methods to find a suitable LOP node.
        
        Returns:
            hou.LopNode or None
        """
        if hou is None:
            return None
        
        # Method 1: Check for selected LOP node
        selected = hou.selectedNodes()
        for node in selected:
            if isinstance(node, hou.LopNode):
                return node
        
        # Method 2: Check for displayed LOP node in network editor
        try:
            pane_tabs = hou.ui.paneTabs()
            for pane in pane_tabs:
                if pane.type() == hou.paneTabType.NetworkEditor:
                    pwd = pane.pwd()
                    if pwd and pwd.childTypeCategory() == hou.lopNodeTypeCategory():
                        # We're in a LOP network, try to find display node
                        for child in pwd.children():
                            if isinstance(child, hou.LopNode) and child.isDisplayFlagSet():
                                return child
        except:
            pass
        
        # Method 3: Look for any LOP network and get its output
        try:
            for node in hou.node('/stage').allSubChildren():
                if isinstance(node, hou.LopNode) and node.isDisplayFlagSet():
                    return node
        except:
            pass
        
        return None
    
    def set_lop_node(self, lop_node):
        """
        Set the LOP node to read the stage from.
        
        Args:
            lop_node: A hou.LopNode object
        """
        self._lop_node = lop_node
        if lop_node is not None:
            try:
                self._stage = lop_node.stage()
            except Exception as e:
                print(f"Failed to get stage from LOP node: {e}")
                self._stage = None
        else:
            self._stage = None
        self._refresh_from_stage()
    
    def refresh(self):
        """
        Refresh the variant list from the current LOP node.
        Call this when the stage may have changed.
        """
        if self._lop_node is not None:
            try:
                self._stage = self._lop_node.stage()
            except:
                self._stage = None
        self._refresh_from_stage()
    
    def _rebuild_list(self):
        """Rebuild the tree widget from _variant_prims data in hierarchy"""
        self.variant_tree.clear()
        self._path_to_item = {}
        
        # Sort prims by path to ensure parents come before children
        sorted_prims = sorted(self._variant_prims, key=lambda p: p["path"])
        
        for prim_data in sorted_prims:
            path = prim_data["path"]
            count = len(prim_data["variant_sets"])
            sets_str = ", ".join(prim_data["variant_sets"])
            
            # Parse path into components (e.g., "/Kitchen/assets/Ball" -> ["Kitchen", "assets", "Ball"])
            path_parts = [p for p in path.split("/") if p]
            
            if not path_parts:
                continue
            
            # Build tree hierarchy
            parent_item = None
            current_path = ""
            
            for i, part in enumerate(path_parts):
                current_path += "/" + part
                is_last = (i == len(path_parts) - 1)
                
                if current_path in self._path_to_item:
                    # Node already exists
                    parent_item = self._path_to_item[current_path]
                else:
                    # Create new tree item
                    item = QtWidgets.QTreeWidgetItem()
                    
                    if is_last:
                        # This is the actual prim with variants
                        item.setText(0, f"{part}  ({count})")
                        item.setToolTip(0, f"Path: {path}\nVariant Sets: {sets_str}")
                        item.setData(0, QtCore.Qt.UserRole, prim_data)
                        # Mark as variant prim for styling
                        item.setData(0, QtCore.Qt.UserRole + 1, True)
                    else:
                        # Intermediate path node (no variants at this level)
                        item.setText(0, part)
                        item.setToolTip(0, f"Path: {current_path}")
                        item.setData(0, QtCore.Qt.UserRole, None)
                        item.setData(0, QtCore.Qt.UserRole + 1, False)
                        # Grey out intermediate nodes
                        item.setForeground(0, QtGui.QColor(128, 128, 128))
                    
                    # Add to parent or root
                    if parent_item is None:
                        self.variant_tree.addTopLevelItem(item)
                    else:
                        parent_item.addChild(item)
                    
                    self._path_to_item[current_path] = item
                    parent_item = item
        
        # Auto-expand all levels by default
        self.variant_tree.expandAll()
    
    def _expand_levels(self, levels):
        """Expand tree items up to the specified depth level"""
        def expand_recursive(item, current_level):
            if current_level < levels:
                item.setExpanded(True)
                for i in range(item.childCount()):
                    expand_recursive(item.child(i), current_level + 1)
        
        for i in range(self.variant_tree.topLevelItemCount()):
            expand_recursive(self.variant_tree.topLevelItem(i), 0)
    
    def _apply_filter(self, text):
        """Filter the tree based on search text, showing matching items and their parents"""
        text = text.lower()
        
        def filter_item(item):
            """Recursively filter items. Returns True if item or any child matches."""
            prim_data = item.data(0, QtCore.Qt.UserRole)
            
            # Check if this item matches
            item_matches = False
            if prim_data:
                path = prim_data["path"].lower()
                sets_str = " ".join(prim_data["variant_sets"]).lower()
                item_matches = text in path or text in sets_str
            else:
                # Intermediate node - check if name matches
                item_matches = text in item.text(0).lower()
            
            # Check children
            child_matches = False
            for i in range(item.childCount()):
                if filter_item(item.child(i)):
                    child_matches = True
            
            # Show item if it matches or any child matches
            should_show = (not text) or item_matches or child_matches
            item.setHidden(not should_show)
            
            # Expand items with matching children
            if child_matches and text:
                item.setExpanded(True)
            
            return item_matches or child_matches
        
        # Apply filter to all top-level items
        for i in range(self.variant_tree.topLevelItemCount()):
            filter_item(self.variant_tree.topLevelItem(i))
    
    def _on_selection_changed(self):
        """Handle selection change in variant tree"""
        selected = self.variant_tree.selectedItems()

        # Filter to only items with variant data (not intermediate nodes)
        variant_items = [item for item in selected if item.data(0, QtCore.Qt.UserRole) is not None]
        count = len(variant_items)

        # Collect prim paths for viewport selection
        prim_paths = []
        for item in selected:
            prim_data = item.data(0, QtCore.Qt.UserRole)
            if prim_data and "path" in prim_data:
                prim_paths.append(prim_data["path"])
            else:
                # For intermediate nodes, find the path from _path_to_item
                for path, tree_item in self._path_to_item.items():
                    if tree_item is item:
                        prim_paths.append(path)
                        break

        # Highlight selected prims in viewport
        if prim_paths:
            highlight_prims_in_viewport(prim_paths)

        # Update right pane with selected prim details
        if count == 1:
            prim_data = variant_items[0].data(0, QtCore.Qt.UserRole)
            self._update_details_pane(prim_data)
            # Emit signal with the selected prim path
            self.primPathChanged.emit(prim_data["path"])
        else: #count == 0
            self._clear_details_pane()
            # Emit empty string when no selection
            self.primPathChanged.emit("")
    
    def _get_selected_paths(self):
        """Get the list of currently selected prim paths."""
        selected_paths = []
        for item in self.variant_tree.selectedItems():
            prim_data = item.data(0, QtCore.Qt.UserRole)
            if prim_data and "path" in prim_data:
                selected_paths.append(prim_data["path"])
            else:
                # For intermediate nodes, find the path from _path_to_item
                for path, tree_item in self._path_to_item.items():
                    if tree_item is item:
                        selected_paths.append(path)
                        break
        return selected_paths
    
    def _restore_selection(self, paths):
        """Restore selection to items matching the given paths."""
        if not paths:
            return
        
        self.variant_tree.blockSignals(True)
        try:
            for path in paths:
                if path in self._path_to_item:
                    self._path_to_item[path].setSelected(True)
        finally:
            self.variant_tree.blockSignals(False)
        
        # Trigger selection changed to update details pane
        if paths:
            self._on_selection_changed()
    
    def set_stage(self, stage):
        """
        Set the USD stage to inspect.

        Args:
            stage: A Usd.Stage object or None
        """
        # Save current selection before refreshing
        selected_paths = self._get_selected_paths()

        self._stage = stage
        self._refresh_from_stage()

        # Restore selection after rebuild
        self._restore_selection(selected_paths)
    
    def _refresh_from_stage(self):
        """
        Scan the stage for prims with variant sets and populate the list.
        """
        if self._stage is None:
            self._variant_prims = []
            self._rebuild_list()
            self._clear_details_pane()
            return
        
        self._variant_prims = []
        
        # Traverse stage and find all prims with variant sets
        for prim in self._stage.Traverse():
            variant_sets = prim.GetVariantSets()
            set_names = variant_sets.GetNames()
            if set_names:
                self._variant_prims.append({
                    "path": str(prim.GetPath()),
                    "variant_sets": list(set_names),
                    "prim": prim,  # Keep reference for details
                })
        
        self._rebuild_list()
    
    def _clear_details_pane(self):
        """Clear all details from the right pane"""
        self.path_label.setText("(No selection)")
        self.copy_path_label.setVisible(False)
        
        # Show placeholder message
        self.placeholder_label.setText("Please select a prim")
        self.placeholder_label.setVisible(True)
        
        # Hide details and bottom bar
        self.details_scroll.setVisible(False)
        self.bottom_bar.setVisible(False)
        
        # Clear variant sets
        self.variant_sets_folder.clear_widgets()
        self._variant_set_rows = []
        
        # Clear properties
        self.properties_folder.clear_widgets()
        self._property_widgets = []
        
        # Clear layers
        self.layer_folder.clear_widgets()
        self._layer_widgets = []
        self.layer_folder.set_title("Layer Stack")
        
        # Clear refs
        self.refs_folder.clear_widgets()
        self._ref_widgets = []
    
    def _show_multi_selection_summary(self, selected_items):
        """Show summary for multiple selected prims"""
        self.path_label.setText(f"({len(selected_items)} prims selected)")
        
        # Clear and show aggregate info
        self.variant_sets_folder.clear_widgets()
        self._variant_set_rows = []
        
        # Collect all variant sets across selection
        all_sets = set()
        for item in selected_items:
            prim_data = item.data(0, QtCore.Qt.UserRole)
            if prim_data:
                all_sets.update(prim_data.get("variant_sets", []))
        
        if all_sets:
            summary_label = QtWidgets.QLabel(f"Variant sets in selection: {', '.join(sorted(all_sets))}")
            summary_label.setWordWrap(True)
            self.variant_sets_folder.add_widget(summary_label)
        
        # Clear other sections
        self.properties_folder.clear_widgets()
        self._property_widgets = []
        self.layer_folder.clear_widgets()
        self._layer_widgets = []
        self.refs_folder.clear_widgets()
        self._ref_widgets = []
    
    def _update_details_pane(self, prim_data):
        """
        Update the right pane with details from the selected prim.

        Args:
            prim_data: Dict with 'path', 'variant_sets', and 'prim' keys
        """
        prim = prim_data.get("prim")
        if prim is None or not prim.IsValid():
            self._clear_details_pane()
            return

        # Get variant set names from prim_data (cached during traversal)
        set_names = prim_data.get("variant_sets", [])

        if not set_names:
            # Prim has no variant sets - show message
            self.path_label.setText(prim_data["path"])
            self.copy_path_label.setVisible(True)

            # Show placeholder message
            self.placeholder_label.setText("There are no variants to show for this prim")
            self.placeholder_label.setVisible(True)

            # Hide details and bottom bar
            self.details_scroll.setVisible(False)
            self.bottom_bar.setVisible(False)
            return

        # Prim has variant sets - show details
        # Hide placeholder and show details
        self.placeholder_label.setVisible(False)
        self.details_scroll.setVisible(True)
        self.bottom_bar.setVisible(True)

        # Update path label
        self.path_label.setText(prim_data["path"])
        self.copy_path_label.setVisible(True)

        # ─────────────────────────────────────────────────────────────────────
        # Variant Sets
        # ─────────────────────────────────────────────────────────────────────
        self.variant_sets_folder.clear_widgets()
        self._variant_set_rows = []

        # Get variant sets object from prim for detailed queries
        variant_sets = prim.GetVariantSets()

        if set_names:
            for set_name in set_names:
                vs = variant_sets.GetVariantSet(set_name)
                current_selection = vs.GetVariantSelection()
                choices = vs.GetVariantNames()

                # Show set name and current selection as normal text
                set_label = QtWidgets.QLabel(f"{set_name}: {current_selection or '(none)'}")
                set_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-bottom: 2px;")
                self.variant_sets_folder.add_widget(set_label)

                # Create a vertical list for variants
                variants_widget = QtWidgets.QWidget()
                variants_layout = QtWidgets.QVBoxLayout(variants_widget)
                variants_layout.setContentsMargins(4, 4, 4, 4)
                variants_layout.setSpacing(4)

                if choices:
                    for choice in choices:
                        option_row = QtWidgets.QWidget()
                        option_layout = QtWidgets.QHBoxLayout(option_row)
                        option_layout.setContentsMargins(0, 0, 0, 0)
                        option_layout.setSpacing(8)

                        # Add a list marker as part of the label text
                        option_label = QtWidgets.QLabel(f"\u2022 {choice}")
                        option_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                        if choice == current_selection:
                            option_label.setStyleSheet("font-weight: bold;")
                        option_layout.addWidget(option_label)

                        option_layout.addStretch()

                        switch_btn = QtWidgets.QPushButton("Switch")
                        switch_btn.setToolTip(f"Create Set Variant node for setting {set_name} to '{choice}'.\n\nThis will create a new node in the LOP network to set the variant. The variant manager is automatically set to use the created node. To undo this, delete the set variant node from the LOP network and revert the LOP path of the variant manager back to the original node.")
                        switch_btn.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips)
                        switch_btn.setProperty("prim_path", prim_data["path"])
                        switch_btn.setProperty("variant_set", set_name)
                        switch_btn.setProperty("variant_choice", choice)
                        switch_btn.clicked.connect(self._on_switch_variant_clicked)
                        option_layout.addWidget(switch_btn)

                        variants_layout.addWidget(option_row)
                else:
                    no_options_label = QtWidgets.QLabel("(no options)")
                    variants_layout.addWidget(no_options_label)

                variants_layout.addStretch()
                self.variant_sets_folder.add_widget(variants_widget)
                self._variant_set_rows.append(variants_widget)
        else:
            no_sets_label = QtWidgets.QLabel("(No variant sets)")
            self.variant_sets_folder.add_widget(no_sets_label)
        
        # ─────────────────────────────────────────────────────────────────────
        # Properties (Metadata)
        # ─────────────────────────────────────────────────────────────────────
        self.properties_folder.clear_widgets()
        self._property_widgets = []
        
        # Collect prim metadata
        properties = []
        
        # Type
        prim_type = prim.GetTypeName()
        if prim_type:
            properties.append(("Type:", prim_type))
        
        # Kind
        try:
            from pxr import Kind
            model = prim.GetModel() if hasattr(prim, 'GetModel') else None
            if model:
                kind = model.GetKind()
                if kind:
                    properties.append(("Kind:", kind))
        except:
            pass
        
        # Custom metadata
        try:
            metadata = prim.GetAllMetadata()
            for key in sorted(metadata.keys()):
                if key not in ('typeName', 'specifier', 'kind'):  # Skip already shown
                    value = metadata[key]
                    if isinstance(value, str) and len(value) < 100:
                        properties.append((f"{key}:", value))
                    elif not isinstance(value, (dict, list)):
                        properties.append((f"{key}:", str(value)[:100]))
        except:
            pass
        
        # Asset info
        try:
            asset_info = prim.GetAssetInfo()
            if asset_info:
                for key, value in asset_info.items():
                    properties.append((f"Asset {key}:", str(value)))
        except:
            pass
        
        # Add property rows
        for prop_name, prop_value in properties:
            prop_row = QtWidgets.QWidget()
            prop_layout = QtWidgets.QHBoxLayout(prop_row)
            prop_layout.setContentsMargins(0, 0, 0, 0)
            prop_layout.setSpacing(8)
            
            name_label = QtWidgets.QLabel(prop_name)
            name_label.setMinimumWidth(100)
            prop_layout.addWidget(name_label)
            
            value_label = QtWidgets.QLabel(str(prop_value))
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            prop_layout.addWidget(value_label, 1)
            
            self.properties_folder.add_widget(prop_row)
            self._property_widgets.append(prop_row)
        
        if not properties:
            no_props = QtWidgets.QLabel("  (No metadata)")
            self.properties_folder.add_widget(no_props)
            self._property_widgets.append(no_props)
        
        # ─────────────────────────────────────────────────────────────────────
        # Layer Stack
        # ─────────────────────────────────────────────────────────────────────
        self.layer_folder.clear_widgets()
        self._layer_widgets = []
        
        try:
            # Get prim stack to find which layers define this prim
            prim_stack = prim.GetPrimStack()
            layers = []
            for prim_spec in prim_stack:
                layer = prim_spec.layer
                layer_name = layer.GetDisplayName() or layer.identifier.split("/")[-1]
                layers.append(layer_name)
            
            self.layer_folder.set_title(f"Layer Stack ({len(layers)} layers)")
            
            for layer_name in layers:
                layer_label = QtWidgets.QLabel(f"  • {layer_name}")
                layer_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                self.layer_folder.add_widget(layer_label)
                self._layer_widgets.append(layer_label)
        except Exception as e:
            error_label = QtWidgets.QLabel(f"  Error: {e}")
            self.layer_folder.add_widget(error_label)
            self._layer_widgets.append(error_label)
        
        # ─────────────────────────────────────────────────────────────────────
        # References & Payloads
        # ─────────────────────────────────────────────────────────────────────
        self.refs_folder.clear_widgets()
        self._ref_widgets = []
        
        refs_and_payloads = []
        
        try:
            # Get references
            refs_api = prim.GetReferences()
            prim_spec = self._stage.GetRootLayer().GetPrimAtPath(prim.GetPath())
            if prim_spec:
                # Check for references
                if hasattr(prim_spec, 'referenceList'):
                    for ref in prim_spec.referenceList.GetAddedOrExplicitItems():
                        ref_path = ref.assetPath if hasattr(ref, 'assetPath') else str(ref)
                        refs_and_payloads.append(f"Reference: {ref_path}")
                
                # Check for payloads
                if hasattr(prim_spec, 'payloadList'):
                    for payload in prim_spec.payloadList.GetAddedOrExplicitItems():
                        payload_path = payload.assetPath if hasattr(payload, 'assetPath') else str(payload)
                        loaded = "loaded" if prim.IsLoaded() else "unloaded"
                        refs_and_payloads.append(f"Payload: {payload_path} ({loaded})")
        except:
            pass
        
        # Also check composition arcs via PrimIndex
        try:
            prim_index = prim.GetPrimIndex()
            for node in prim_index.rootNode.children:
                arc_type = str(node.arcType)
                if "Reference" in arc_type or "Payload" in arc_type:
                    layer_path = node.layerStack.layers[0].identifier if node.layerStack.layers else "unknown"
                    arc_str = f"{arc_type}: {layer_path}"
                    if arc_str not in refs_and_payloads:
                        refs_and_payloads.append(arc_str)
        except:
            pass
        
        if refs_and_payloads:
            for ref_str in refs_and_payloads:
                ref_label = QtWidgets.QLabel(f"  • {ref_str}")
                ref_label.setWordWrap(True)
                ref_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                self.refs_folder.add_widget(ref_label)
                self._ref_widgets.append(ref_label)
        else:
            no_refs = QtWidgets.QLabel("  (No references or payloads)")
            self.refs_folder.add_widget(no_refs)
            self._ref_widgets.append(no_refs)

    def _copy_path_to_clipboard(self):
        """Copy the current prim path to clipboard"""
        path = self.path_label.text()
        if path and not path.startswith("("):
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(path)

    def _copy_details_to_clipboard(self):
        """Copy the current details pane content to clipboard as text."""
        lines = []
        
        # Prim path
        prim_path = self.path_label.text()
        if prim_path and prim_path != "(No selection)":
            lines.append(f"Prim Path: {prim_path}")
            lines.append("")
        
        # Variant Sets
        if self._variant_set_rows:
            lines.append("=== Variant Sets ===")
            for page_widget in self._variant_set_rows:
                set_name = getattr(page_widget, 'set_name', '')
                current_val = getattr(page_widget, 'current_selection', '')
                lines.append(f"  {set_name}: {current_val}")
                # Include choices if available
                if hasattr(page_widget, 'variant_choices') and page_widget.variant_choices:
                    lines.append(f"    Options: {', '.join(page_widget.variant_choices)}")
            lines.append("")
        
        # Properties
        if self._property_widgets:
            lines.append("=== Properties ===")
            for widget in self._property_widgets:
                layout = widget.layout()
                if layout and layout.count() >= 2:
                    name_item = layout.itemAt(0)
                    value_item = layout.itemAt(1)
                    if name_item and value_item:
                        name_widget = name_item.widget()
                        value_widget = value_item.widget()
                        if name_widget and value_widget:
                            name = name_widget.text() if hasattr(name_widget, 'text') else ""
                            value = value_widget.text() if hasattr(value_widget, 'text') else ""
                            lines.append(f"  {name} {value}")
                elif isinstance(widget, QtWidgets.QLabel):
                    lines.append(f"  {widget.text()}")
            lines.append("")
        
        # Layer Stack
        if self._layer_widgets:
            lines.append("=== Layer Stack ===")
            for widget in self._layer_widgets:
                if isinstance(widget, QtWidgets.QLabel):
                    lines.append(widget.text())
            lines.append("")
        
        # References & Payloads
        if self._ref_widgets:
            lines.append("=== References & Payloads ===")
            for widget in self._ref_widgets:
                if isinstance(widget, QtWidgets.QLabel):
                    lines.append(widget.text())
        
        # Copy to clipboard
        text = "\n".join(lines)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

    def set_source_lop_node_callback(self, callback):
        """
        Set a callback function that returns the source LOP node to insert after.
        
        Args:
            callback: A callable that returns a hou.LopNode or None
        """
        self._get_source_lop_node_callback = callback
    
    def _get_source_lop_node(self):
        """
        Get the source LOP node to insert new nodes after.
        Uses the callback from the main panel if available, then falls back to internal reference.
        """
        # Try the callback first
        if self._get_source_lop_node_callback is not None:
            node = self._get_source_lop_node_callback()
            if node is not None:
                return node
        # Fallback to internal reference
        return self._lop_node

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