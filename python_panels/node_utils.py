"""
Node creation utilities for Variant Manager by havocado
Handles creation and management of LOP nodes in Houdini
"""

try:
    import hou
    HOU_AVAILABLE = True
except ImportError:
    hou = None
    HOU_AVAILABLE = False


def is_node_valid(node):
    """
    Check if a Houdini node reference is alive and usable.

    A deleted node is not None but throws hou.ObjectWasDeleted on access.

    Args:
        node: A Houdini node reference, or None.

    Returns:
        True if the node is not None and still exists in Houdini.
    """
    if node is None:
        return False
    if not HOU_AVAILABLE:
        return False
    try:
        node.path()
        return True
    except hou.ObjectWasDeleted:
        return False


def create_set_variant_node(lop_node, node_name=None):
    """
    Create a Set Variant LOP node after the specified LOP node.
    
    Args:
        lop_node: The LOP node to insert after. The new node will be 
                  connected to this node's output and become the new display node.
        node_name: Optional name for the new node. If None, uses "set_variant".
    
    Returns:
        The newly created Set Variant node, or None if creation failed.
    
    Raises:
        ValueError: If lop_node is None or invalid.
        RuntimeError: If Houdini is not available.
    """
    if not HOU_AVAILABLE:
        raise RuntimeError("Houdini is not available")
    
    if not is_node_valid(lop_node):
        raise ValueError("lop_node is None or no longer valid")
    
    # Get the parent network
    parent_network = lop_node.parent()
    if parent_network is None:
        raise ValueError("Could not get parent network from lop_node")
    
    # Generate unique node name
    if node_name is None:
        node_name = "set_variant"
    
    # Create the Set Variant node
    try:
        set_variant_node = parent_network.createNode("setvariant", node_name)
    except Exception as e:
        raise RuntimeError(f"Failed to create setvariant node: {e}")
    
    # Position the new node below the input node
    input_pos = lop_node.position()
    set_variant_node.setPosition(hou.Vector2(input_pos[0], input_pos[1] - 1.0))
    
    # Connect the new node to the input node
    set_variant_node.setInput(0, lop_node)
    
    # Find any nodes that were connected to the output of lop_node
    # and reconnect them to the new node
    for connection in lop_node.outputConnections():
        output_node = connection.outputNode()
        input_index = connection.inputIndex()
        # Skip the node we just created
        if output_node != set_variant_node:
            output_node.setInput(input_index, set_variant_node)
    
    # Set the display flag on the new node
    set_variant_node.setDisplayFlag(True)
    
    return set_variant_node


def configure_set_variant_node(node, prim_path, variant_set_name, variant_selection):
    """
    Configure a Set Variant node with the specified parameters.
    
    Args:
        node: The Set Variant LOP node to configure.
        prim_path: The USD prim path (e.g., "/Kitchen/assets/Ball").
        variant_set_name: The name of the variant set (e.g., "modelingVariant").
        variant_selection: The variant to select (e.g., "red").
    
    Returns:
        True if configuration succeeded, False otherwise.
    """
    if not HOU_AVAILABLE:
        return False
    
    if not is_node_valid(node):
        return False
    
    try:
        # Set the prim pattern (primitives parameter - first entry in multi-parm)
        prim_pattern_parm = node.parm("primpattern1")
        if prim_pattern_parm:
            prim_pattern_parm.set(prim_path)
        
        # Set the variant set name (first entry in multi-parm)
        variantset_parm = node.parm("variantset1")
        if variantset_parm:
            variantset_parm.set(variant_set_name)
        
        # Set the variant selection (first entry in multi-parm)
        variant_parm = node.parm("variantname1")
        if variant_parm:
            variant_parm.set(variant_selection)
        
        return True
    except Exception as e:
        print(f"Failed to configure set variant node: {e}")
        return False


def get_node_info(node):
    """
    Get information about a node for debugging.
    
    Args:
        node: A Houdini node.
    
    Returns:
        Dict with node information.
    """
    if not HOU_AVAILABLE or node is None:
        return {}
    
    try:
        return {
            "path": node.path(),
            "name": node.name(),
            "type": node.type().name(),
            "position": tuple(node.position()),
            "is_display": node.isDisplayFlagSet() if hasattr(node, 'isDisplayFlagSet') else None,
        }
    except Exception as e:
        return {"error": str(e)}


def jump_to_node(node):
    """
    Navigate to a node in the network editor and select it.
    This will also show the node's parameters in the Parameter Pane.
    
    Args:
        node: A Houdini node to jump to.
    
    Returns:
        True if successful, False otherwise.
    """
    if not HOU_AVAILABLE or node is None:
        return False
    
    try:
        # Select the node (this also updates the Parameter Pane)
        node.setCurrent(True, clear_all_selected=True)
        
        # Find a network editor and navigate to the node
        for pane in hou.ui.paneTabs():
            if pane.type() == hou.paneTabType.NetworkEditor:
                pane.setCurrentNode(node)
                pane.homeToSelection()
                break
        
        return True
    except Exception as e:
        print(f"Failed to jump to node: {e}")
        return False
