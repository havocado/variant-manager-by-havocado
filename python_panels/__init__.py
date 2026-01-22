"""
Variant Manager by havocado - USD Variant Inspector Panel for Houdini
"""
from .variant_manager_by_havocado import VariantManagerPanel, createInterface
from .widgets import CollapsibleFolder, VariantSetRow, ComparisonPanelWidget
from .inspector_tab import InspectorTab
from .comparison_tab import ComparisonTab
from .analysis_tab import AnalysisTab

__all__ = [
    'VariantManagerPanel',
    'createInterface',
    'CollapsibleFolder',
    'VariantSetRow',
    'ComparisonPanelWidget',
    'InspectorTab',
    'ComparisonTab',
    'AnalysisTab',
]
