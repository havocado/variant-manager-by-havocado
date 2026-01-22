"""
Thumbnail Generator for Variant Manager by havocado
Handles async thumbnail generation queue with QTimer orchestration
"""
import os
from PySide6 import QtCore, QtGui

from .viewport_capture import ViewportCaptureService, CaptureException


class ThumbnailGenerator(QtCore.QObject):
    """
    Manages asynchronous thumbnail generation queue.

    Processes thumbnail requests one at a time using QTimer to avoid
    blocking the UI. Emits signals when thumbnails are ready.
    """

    # Signals
    thumbnail_generated = QtCore.Signal(int, QtGui.QPixmap, str)  # index, pixmap, cache_key
    generation_error = QtCore.Signal(int, str)  # index, error_message
    queue_completed = QtCore.Signal()

    # Timing configuration
    TIMER_INTERVAL = 50  # ms between generations
    GENERATION_TIMEOUT = 2000  # ms max per thumbnail (not implemented yet)

    def __init__(self, viewport_service, parent=None):
        """
        Initialize the thumbnail generator.

        Args:
            viewport_service: ViewportCaptureService instance for capturing thumbnails
            parent: Optional parent QObject
        """
        super(ThumbnailGenerator, self).__init__(parent)

        self.viewport_service = viewport_service
        self._queue = []  # List of (index, prim_path, variant_set_name, variant_value, cache_key)
        self._is_busy = False
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._generate_next)
        self._timer.setSingleShot(True)

    def queue_item(self, index, prim_path, variant_set_name, variant_value, cache_key):
        """
        Add a thumbnail generation request to the queue.

        Args:
            index: Index for UI tracking (which panel to update)
            prim_path: USD prim path
            variant_set_name: Name of the variant set
            variant_value: Variant value to apply
            cache_key: Unique cache key for this variant combination
        """
        request = (index, prim_path, variant_set_name, variant_value, cache_key)

        # Don't queue duplicates (same cache_key)
        for queued_item in self._queue:
            if queued_item[4] == cache_key:  # Check cache_key
                return

        self._queue.append(request)

        # Start processing if not already busy
        if not self._is_busy:
            self.process_queue()

    def process_queue(self):
        """Start processing the queue if not already busy."""
        if not self._is_busy and self._queue:
            self._timer.start(self.TIMER_INTERVAL)

    def _generate_next(self):
        """Internal: Generate the next thumbnail in the queue."""
        if not self._queue:
            self._is_busy = False
            self.queue_completed.emit()
            return

        self._is_busy = True

        # Pop next item from queue (FIFO)
        index, prim_path, variant_set_name, variant_value, cache_key = self._queue.pop(0)

        temp_file = None
        try:
            # Capture thumbnail
            temp_file = self.viewport_service.capture(
                prim_path,
                variant_set_name,
                variant_value
            )

            # Load QPixmap from temp file
            pixmap = QtGui.QPixmap(temp_file)

            if pixmap.isNull():
                raise Exception("Failed to load pixmap from captured file")

            # Emit success signal
            self.thumbnail_generated.emit(index, pixmap, cache_key)

        except CaptureException as e:
            # Emit error signal
            self.generation_error.emit(index, str(e))
        except Exception as e:
            # Emit error signal for unexpected errors
            self.generation_error.emit(index, f"Unexpected error: {str(e)}")
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

            # Schedule next item
            self._is_busy = False
            if self._queue:
                self._timer.start(self.TIMER_INTERVAL)
            else:
                self.queue_completed.emit()

    def cancel_all(self):
        """Clear the queue and stop processing."""
        self._queue.clear()
        self._timer.stop()
        self._is_busy = False

    def is_busy(self):
        """Return True if currently generating a thumbnail."""
        return self._is_busy

    def queue_length(self):
        """Return the number of items in the queue."""
        return len(self._queue)
