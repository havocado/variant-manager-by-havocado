"""
Thumbnail Generation System for Variant Manager by havocado

This module provides thumbnail generation for USD variants using viewport captures.
Features include:
- Non-blocking async thumbnail generation
- Dedicated hidden scene viewer

Main API:
    ThumbnailManager - Facade for requesting thumbnails

Usage:
    from thumbnail import ThumbnailManager

    manager = ThumbnailManager(source_lop_node)
    manager.thumbnail_ready.connect(on_thumbnail_ready)
    manager.request_thumbnail(0, "/World/Chair", "modelingVariant", "red")
"""

from .thumbnail_manager import ThumbnailManager
from .viewport_capture import ViewportCaptureService, CaptureException
from .thumbnail_generator import ThumbnailGenerator

__all__ = [
    'ThumbnailManager',
    'ViewportCaptureService',
    'ThumbnailGenerator',
    'CaptureException',
]
