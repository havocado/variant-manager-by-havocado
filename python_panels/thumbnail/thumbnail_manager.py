"""
Thumbnail Manager for Variant Manager by havocado
Facade for thumbnail generation system with cache management
"""
from PySide6 import QtCore, QtGui

from .viewport_capture import ViewportCaptureService, CaptureException
from .thumbnail_generator import ThumbnailGenerator


class ThumbnailManager(QtCore.QObject):
    """
    Facade for the thumbnail generation system.

    Coordinates between the UI and the thumbnail generator.
    Provides a simple API for requesting thumbnails.
    """

    # Signals
    thumbnail_ready = QtCore.Signal(int, QtGui.QPixmap)  # index, pixmap
    generation_failed = QtCore.Signal(int, str)  # index, error_message

    def __init__(self, source_lop_node, parent=None):
        """
        Initialize the thumbnail manager.

        Args:
            source_lop_node: The LOP node to use as the base for thumbnail generation
            parent: Optional parent QObject

        Raises:
            RuntimeError: If initialization fails
        """
        super(ThumbnailManager, self).__init__(parent)

        # Initialize viewport capture service
        try:
            self._viewport_service = ViewportCaptureService(source_lop_node)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize viewport capture service: {e}")

        # Initialize thumbnail generator
        self._generator = ThumbnailGenerator(self._viewport_service, parent=self)

        # Connect generator signals
        self._generator.thumbnail_generated.connect(self._on_thumbnail_generated)
        self._generator.generation_error.connect(self._on_generation_error)

    def request_thumbnail(self, index, prim_path, variant_set_name, variant_value):
        """
        Request a thumbnail for a specific variant.

        Args:
            index: Index for UI tracking (which panel to update)
            prim_path: USD prim path
            variant_set_name: Name of the variant set
            variant_value: Variant value to apply
        """
        # Queue for generation (no caching)
        cache_key = f"{prim_path}|{variant_set_name}|{variant_value}"
        self._generator.queue_item(
            index,
            prim_path,
            variant_set_name,
            variant_value,
            cache_key
        )

    def cancel_pending(self):
        """Cancel all queued thumbnail generations."""
        self._generator.cancel_all()

    def _on_thumbnail_generated(self, index, pixmap, cache_key):
        """
        Internal callback when thumbnail generation succeeds.

        Args:
            index: UI index
            pixmap: Generated QPixmap
            cache_key: Cache key for this thumbnail (unused, kept for compatibility)
        """
        # Forward to UI (no caching)
        self.thumbnail_ready.emit(index, pixmap)

    def _on_generation_error(self, index, error_message):
        """
        Internal callback when thumbnail generation fails.

        Args:
            index: UI index
            error_message: Error description
        """
        # Forward error to UI
        self.generation_failed.emit(index, error_message)

    def cleanup(self):
        """Clean up resources."""
        self.cancel_pending()

        if self._viewport_service:
            self._viewport_service.cleanup()
            self._viewport_service = None

    def __del__(self):
        """Destructor - ensure cleanup happens."""
        self.cleanup()
