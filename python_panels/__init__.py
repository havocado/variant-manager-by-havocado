"""
Variant Manager by havocado - USD Variant Inspector Panel for Houdini
"""
from .variant_manager_by_havocado import VariantManagerPanel, createInterface
from .widgets import ComparisonPanelWidget
from .inspector_tab import InspectorTab
from .comparison_tab import ComparisonTab

__all__ = [
    'VariantManagerPanel',
    'createInterface',
    'ComparisonPanelWidget',
    'InspectorTab',
    'ComparisonTab',
]
