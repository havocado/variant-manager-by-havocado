"""
LOP node discovery and selection utilities for Variant Manager.
"""
import hou
from PySide6 import QtCore

from state import get_state
from node_utils import is_node_valid


class LOPNodeCoordinator(QtCore.QObject):
    """
    Service for discovering and selecting LOP nodes.
    Updates the state singleton directly when selection changes.
    """

    # UI-specific signals (not for state - just for updating UI elements)
    nodesUpdated = QtCore.Signal(list)   # Emits list of available node paths
    errorOccurred = QtCore.Signal(str)   # Emits error message

    def __init__(self, parent=None):
        super(LOPNodeCoordinator, self).__init__(parent)
        self._available_nodes = []

    @property
    def available_nodes(self):
        """Returns list of available LOP node paths."""
        return self._available_nodes

    def refresh_node_list(self):
        """Re-scan all LOP nodes in the scene that have valid stages."""
        nodes = []
        try:
            # Find all LOP networks
            for node in hou.node("/").allSubChildren():
                if node.type().category().name() == "Lop":
                    # Filter out nodes inside locked HDAs
                    if node.isInsideLockedHDA():
                        continue
                    # Filter out internal thumbnail generator nodes
                    if "_thumbnail_generator_internal" in node.name():
                        continue
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

    def select_lop_node_states(self, node_path):
        """
        Select a LOP node by path and update state with node and stage.
        Called when user selects a node from UI, or creates one,
        or when auto-discovering nodes.

        Args:
            node_path: Full path to the LOP node (e.g., "/stage/variant")

        Returns:
            The USD stage if successful, None otherwise
        """
        state = get_state()

        if not node_path:
            state.lop_node = None
            state.stage = None
            return None

        # Get the node and stage
        lop_node = None
        stage = None

        try:
            lop_node = hou.node(node_path)
            if lop_node is None:
                self.errorOccurred.emit(f"Node not found: {node_path}")
            elif lop_node.type().category().name() != "Lop":
                self.errorOccurred.emit(f"Not a LOP node: {node_path}")
                lop_node = None
            else:
                stage = lop_node.stage()
                if stage is None:
                    self.errorOccurred.emit(f"No stage available from: {node_path}")
        except Exception as e:
            self.errorOccurred.emit(f"Error getting stage: {str(e)}")
        
        # Update state - this emits signals that tabs subscribe to
        state.lop_node = lop_node
        state.stage = stage

        return stage
    
    def refresh_current_stage(self):
        """Re-fetch the stage from the currently selected node."""
        state = get_state()
        if is_node_valid(state.lop_node):
            return self.select_lop_node_states(state.lop_node.path())
        return None

    def select_from_network_selection(self):
        """
        Auto-select based on current network editor selection.
        Useful for syncing with user's node selection in Houdini.
        """
        try:
            selected = hou.selectedNodes()
            for node in selected:
                if node.type().category().name() == "Lop":
                    return self.select_lop_node_states(node.path())
        except Exception as e:
            self.errorOccurred.emit(f"Error reading selection: {str(e)}")

        return None

    def discover_initial_node(self):
        """
        Discover and select an initial LOP node from the Houdini context.
        Tries multiple methods to find a suitable LOP node.

        Returns:
            hou.LopNode or None
        """
        try:
            # Method 1: Check for selected LOP node
            selected = hou.selectedNodes()
            for node in selected:
                if isinstance(node, hou.LopNode):
                    self.select_lop_node_states(node.path())
                    return node

            # Method 2: Check for displayed LOP node in network editor
            pane_tabs = hou.ui.paneTabs()
            for pane in pane_tabs:
                if pane.type() == hou.paneTabType.NetworkEditor:
                    pwd = pane.pwd()
                    if pwd and pwd.childTypeCategory() == hou.lopNodeTypeCategory():
                        # We're in a LOP network, try to find display node
                        for child in pwd.children():
                            if isinstance(child, hou.LopNode) and child.isDisplayFlagSet():
                                self.select_lop_node_states(child.path())
                                return child

            # Method 3: Look for any LOP network and get its output
            for node in hou.node('/stage').allSubChildren():
                if isinstance(node, hou.LopNode) and node.isDisplayFlagSet():
                    self.select_lop_node_states(node.path())
                    return node
        except Exception:
            pass

        return None

    def jump_to_node(self):
        """Navigate to the current node in the network editor."""
        state = get_state()
        if not is_node_valid(state.lop_node):
            return

        try:
            node = state.lop_node
            # Find a network editor pane and navigate to the node
            for pane in hou.ui.paneTabs():
                if pane.type() == hou.paneTabType.NetworkEditor:
                    pane.setCurrentNode(node)
                    pane.homeToSelection()
                    break
        except Exception as e:
            self.errorOccurred.emit(f"Error jumping to node: {str(e)}")
