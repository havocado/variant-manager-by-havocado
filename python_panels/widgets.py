"""
Shared widget components for Variant Manager by havocado
"""
from PySide6 import QtWidgets, QtCore, QtGui


# ═══════════════════════════════════════════════════════════════════════════════
# COLLAPSIBLE FOLDER WIDGET (Houdini Parameter Pane Style)
# ═══════════════════════════════════════════════════════════════════════════════

class CollapsibleFolder(QtWidgets.QWidget):
    """Houdini-style collapsible parameter folder"""
    
    def __init__(self, title, parent=None, expanded=True):
        super(CollapsibleFolder, self).__init__(parent)
        self._expanded = expanded
        self._title = title
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = QtWidgets.QFrame()
        self.header.setCursor(QtCore.Qt.PointingHandCursor)
        
        header_layout = QtWidgets.QHBoxLayout(self.header)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(6)
        
        # Toggle arrow
        self.toggle_label = QtWidgets.QLabel("▾" if expanded else "▸")
        self.toggle_label.setFixedWidth(12)
        header_layout.addWidget(self.toggle_label)
        
        # Title
        self.title_label = QtWidgets.QLabel(title)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Right side value/status area
        self.status_label = QtWidgets.QLabel("")
        header_layout.addWidget(self.status_label)
        
        main_layout.addWidget(self.header)
        
        # Content area
        self.content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(20, 4, 4, 4)
        content_layout.setSpacing(2)
        self.content_layout = content_layout
        
        main_layout.addWidget(self.content)
        
        # Set initial state
        self.content.setVisible(expanded)
        
        # Install event filter for click handling
        self.header.mousePressEvent = self._on_header_clicked
    
    def _on_header_clicked(self, event):
        self.toggle()
    
    def toggle(self):
        self._expanded = not self._expanded
        self.content.setVisible(self._expanded)
        self.toggle_label.setText("▾" if self._expanded else "▸")
    
    def set_status(self, text):
        self.status_label.setText(text)
    
    def set_title(self, text):
        """Update the folder title"""
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
# VARIANT SET ROW WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class VariantSetRow(QtWidgets.QWidget):
    """Single variant set row with expand/collapse"""
    
    def __init__(self, name, current_value, has_warning=False, parent=None, expanded=False):
        super(VariantSetRow, self).__init__(parent)
        self._expanded = expanded
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 2, 0, 2)
        main_layout.setSpacing(2)
        
        # Header row
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        # Toggle arrow
        self.toggle_label = QtWidgets.QLabel("▾" if expanded else "▸")
        self.toggle_label.setFixedWidth(12)
        self.toggle_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.toggle_label.mousePressEvent = lambda e: self.toggle()
        header_layout.addWidget(self.toggle_label)
        
        # Variant set name
        name_label = QtWidgets.QLabel(name)
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Current value
        value_label = QtWidgets.QLabel(current_value)
        header_layout.addWidget(value_label)
        
        # Warning icon
        if has_warning:
            warning_label = QtWidgets.QLabel("⚠️")
            warning_label.setToolTip("Dependency warning")
            header_layout.addWidget(warning_label)
        
        # Info icon
        info_label = QtWidgets.QLabel("ℹ️")
        info_label.setToolTip("Click for metadata")
        info_label.setCursor(QtCore.Qt.PointingHandCursor)
        header_layout.addWidget(info_label)
        
        main_layout.addWidget(header)
        
        # Detail content (shown when expanded)
        self.detail_content = QtWidgets.QWidget()
        detail_layout = QtWidgets.QVBoxLayout(self.detail_content)
        detail_layout.setContentsMargins(20, 0, 0, 0)
        detail_layout.setSpacing(2)
        self.detail_layout = detail_layout
        
        main_layout.addWidget(self.detail_content)
        self.detail_content.setVisible(expanded)
    
    def toggle(self):
        self._expanded = not self._expanded
        self.detail_content.setVisible(self._expanded)
        self.toggle_label.setText("▾" if self._expanded else "▸")
    
    def add_detail(self, text, is_warning=False):
        label = QtWidgets.QLabel(text)
        self.detail_layout.addWidget(label)


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

        # Thumbnail display (replaces viewport placeholder)
        self.thumbnail_label = QtWidgets.QLabel("[Viewport]")
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
        
        lock_btn = QtWidgets.QToolButton()
        lock_btn.setText("🔒")
        lock_btn.setToolTip("Pin/lock this view")
        lock_btn.setCheckable(True)
        controls_layout.addWidget(lock_btn)
        
        camera_btn = QtWidgets.QToolButton()
        camera_btn.setText("📷")
        camera_btn.setToolTip("Reset camera")
        controls_layout.addWidget(camera_btn)
        
        focus_btn = QtWidgets.QToolButton()
        focus_btn.setText("🔍")
        focus_btn.setToolTip("Focus/isolate")
        controls_layout.addWidget(focus_btn)
        
        controls_layout.addStretch()

        layout.addWidget(controls)

    def set_variant_name(self, variant_name):
        """Update the variant name displayed in the panel"""
        self.variant_label.setText(variant_name)

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
            self.thumbnail_label.setText("[Viewport]")

    def set_loading(self):
        """Show loading state for thumbnail."""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("[Loading...]")

    def set_failed(self):
        """Show failed state for thumbnail."""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("[Failed]")
