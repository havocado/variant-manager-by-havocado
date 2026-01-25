"""
Shared widget components for Variant Manager by havocado
"""
from PySide6 import QtWidgets, QtCore, QtGui


# ═══════════════════════════════════════════════════════════════════════════════
# SWITCH VARIANT BUTTON
# ═══════════════════════════════════════════════════════════════════════════════

class SwitchVariantButton(QtWidgets.QPushButton):
    """
    Reusable button for switching USD variants.

    Stores prim_path, variant_set, and variant_choice as properties
    for use by click handlers in the parent widget.
    """

    def __init__(self, parent=None):
        super(SwitchVariantButton, self).__init__("Switch", parent)

    def set_variant_context(self, prim_path, variant_set, variant_choice):
        """
        Set the variant context for this button.

        Args:
            prim_path: USD prim path
            variant_set: Variant set name
            variant_choice: Variant choice name
        """
        self.setProperty("prim_path", prim_path)
        self.setProperty("variant_set", variant_set)
        self.setProperty("variant_choice", variant_choice)
        self.setToolTip(
            f"Create Set Variant node for setting {variant_set} to '{variant_choice}'.\n\n"
            "This will create a new node in the LOP network to set the variant. "
            "The variant manager is automatically set to use the created node. "
            "To undo this, delete the set variant node from the LOP network and "
            "revert the LOP path of the variant manager back to the original node."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLE SECTION WIDGET (Non-collapsible)
# ═══════════════════════════════════════════════════════════════════════════════

class SimpleSection(QtWidgets.QWidget):
    """Simple section with title and content area (non-collapsible)"""

    def __init__(self, title, parent=None):
        super(SimpleSection, self).__init__(parent)
        self._title = title

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # Header
        header = QtWidgets.QFrame()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(6)

        # Title
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        main_layout.addWidget(header)

        # Separator line
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(separator)

        # Content area
        self.content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(8, 4, 4, 8)
        content_layout.setSpacing(2)
        self.content_layout = content_layout

        main_layout.addWidget(self.content)

    def set_title(self, text):
        """Update the section title"""
        self._title = text
        self.title_label.setText(text)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)

    def clear_widgets(self):
        """Remove all widgets from the content area"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON PANEL WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class ComparisonPanelWidget(QtWidgets.QFrame):
    """Single comparison panel for side-by-side view"""

    def __init__(self, variant_name, parent=None):
        super(ComparisonPanelWidget, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Variant name
        self.variant_label = QtWidgets.QLabel(variant_name)
        self.variant_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.variant_label)

        # Thumbnail display
        self.thumbnail_label = QtWidgets.QLabel("Click [Preview] button")
        self.thumbnail_label.setMinimumSize(150, 120)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        self.thumbnail_label.setScaledContents(False)  # Preserve aspect ratio
        layout.addWidget(self.thumbnail_label)

        # Control buttons overlay
        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)

        controls_layout.addStretch()

        self.switch_btn = SwitchVariantButton()
        controls_layout.addWidget(self.switch_btn)

        controls_layout.addStretch()

        layout.addWidget(controls)

    def set_variant_name(self, variant_name):
        """Update the variant name displayed in the panel"""
        self.variant_label.setText(variant_name)

    def set_variant_context(self, prim_path, variant_set, variant_choice):
        """
        Set the variant context for the switch button.

        Args:
            prim_path: USD prim path
            variant_set: Variant set name
            variant_choice: Variant choice name
        """
        self.switch_btn.set_variant_context(prim_path, variant_set, variant_choice)

    def set_thumbnail(self, pixmap):
        """
        Set the thumbnail pixmap for this panel.

        Args:
            pixmap: QPixmap to display, or None to show placeholder
        """
        if pixmap and not pixmap.isNull():
            # Scale pixmap to fit while preserving aspect ratio
            label_size = self.thumbnail_label.size()
            scaled_pixmap = pixmap.scaled(
                label_size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.clear()
            self.thumbnail_label.setText("Click [Preview] button")

    def set_loading(self):
        """Show loading state for thumbnail."""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("Click [Preview] button")

    def set_failed(self):
        """Show failed state for thumbnail."""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("[Failed]")
