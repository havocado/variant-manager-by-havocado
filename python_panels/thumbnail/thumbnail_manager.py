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

        # Cache for generated thumbnails: cache_key -> QPixmap
        self._cache = {}

    def request_thumbnail(self, index, prim_path, variant_set_name, variant_value, force_regenerate=False):
        """
        Request a thumbnail for a specific variant.

        Args:
            index: Index for UI tracking (which panel to update)
            prim_path: USD prim path
            variant_set_name: Name of the variant set
            variant_value: Variant value to apply
            force_regenerate: If True, bypass duplicate check and always regenerate
        """
        # Always generate cache_key for caching purposes
        cache_key = f"{prim_path}|{variant_set_name}|{variant_value}"
        self._generator.queue_item(
            index,
            prim_path,
            variant_set_name,
            variant_value,
            cache_key,
            skip_duplicate_check=force_regenerate
        )

    def get_cached_thumbnail(self, prim_path, variant_set_name, variant_value):
        """
        Get a thumbnail from cache without triggering generation.

        Args:
            prim_path: USD prim path
            variant_set_name: Name of the variant set
            variant_value: Variant value to apply

        Returns:
            QPixmap if cached, None if not in cache
        """
        cache_key = f"{prim_path}|{variant_set_name}|{variant_value}"
        print(f"Looking for cache key: {cache_key}")
        print(f"Cache contents: {list(self._cache.keys())}")
        return self._cache.get(cache_key)

    def cancel_pending(self):
        """Cancel all queued thumbnail generations."""
        self._generator.cancel_all()

    def update_source_node(self, source_lop_node):
        """
        Update the source LOP node, preserving cache.

        Cleans up the old viewport service (node + temp dir) and creates
        a new one connected to the new source node.

        Args:
            source_lop_node: The new LOP node to use as the base for thumbnail generation.
                            Can be None to just cleanup without reinitializing.
        """
        # Cancel any pending work
        self.cancel_pending()

        # Cleanup old viewport service (node + temp dir)
        if self._viewport_service:
            self._viewport_service.cleanup()
            self._viewport_service = None

        # Create new viewport service with new node
        if source_lop_node:
            try:
                self._viewport_service = ViewportCaptureService(source_lop_node)
                self._generator.viewport_service = self._viewport_service
            except Exception as e:
                print(f"Failed to update viewport capture service: {e}")
                self._viewport_service = None
                self._generator.viewport_service = None

    def _on_thumbnail_generated(self, index, pixmap, cache_key):
        """
        Internal callback when thumbnail generation succeeds.

        Args:
            index: UI index
            pixmap: Generated QPixmap
            cache_key: Cache key for this thumbnail
        """
        # Store in cache if cache_key is valid
        if cache_key is not None:
            print(f"Caching thumbnail with key: {cache_key}")
            self._cache[cache_key] = pixmap
        
        print(f"Cache contents after generation: {list(self._cache.keys())}")

        # Forward to UI
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
        self._cache.clear()

        if self._viewport_service:
            self._viewport_service.cleanup()
            self._viewport_service = None

    def __del__(self):
        """Destructor - ensure cleanup happens."""
        self.cleanup()
