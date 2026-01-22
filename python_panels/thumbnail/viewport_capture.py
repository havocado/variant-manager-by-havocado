"""
Viewport Capture Service for Variant Manager by havocado
Handles viewport setup, scene isolation, and thumbnail capture
"""
import os
import tempfile

try:
    import hou
    from husd import assetutils
    HOU_AVAILABLE = True
except ImportError:
    hou = None
    assetutils = None
    HOU_AVAILABLE = False

from node_utils import create_set_variant_node, configure_set_variant_node


class CaptureException(Exception):
    """Exception raised when thumbnail capture fails"""
    pass


class ViewportCaptureService:
    """
    Manages viewport setup and thumbnail capture for USD variants.

    Uses a dedicated hidden scene viewer and persistent setvariant node
    to generate thumbnails without affecting the user's viewport.
    """

    # Configuration constants
    THUMBNAIL_RESOLUTION = (512, 384)  # 4:3 aspect ratio to match typical viewports
    BACKGROUND_COLOR = (0.5, 0.5, 0.5)  # Mid-gray

    def __init__(self, source_lop_node):
        """
        Initialize the viewport capture service.

        Args:
            source_lop_node: The LOP node to create the setvariant node after.
                            This is typically the user's current working LOP node.

        Raises:
            RuntimeError: If Houdini is not available or initialization fails.
        """
        if not HOU_AVAILABLE:
            raise RuntimeError("Houdini is not available")

        if source_lop_node is None:
            raise ValueError("source_lop_node cannot be None")

        self.source_lop_node = source_lop_node
        self.variant_node = None
        self.temp_directory = None

        try:
            # Create persistent setvariant node for thumbnail generation
            self.variant_node = create_set_variant_node(
                source_lop_node,
                node_name="_thumbnail_generator_internal"
            )

            if self.variant_node is None:
                raise RuntimeError("Failed to create setvariant node for thumbnails")

            # Create temp directory for thumbnail files
            self.temp_directory = os.path.join(
                tempfile.gettempdir(),
                f"houdini_variant_thumbs_{os.getpid()}"
            )
            os.makedirs(self.temp_directory, exist_ok=True)

        except Exception as e:
            # Clean up on initialization failure
            self.cleanup()
            raise RuntimeError(f"Failed to initialize viewport capture service: {e}")


    def capture(self, prim_path, variant_set_name, variant_value):
        """
        Capture a thumbnail for the specified variant using the main viewport.

        Args:
            prim_path: USD prim path (e.g., "/World/Chair")
            variant_set_name: Name of the variant set (e.g., "modelingVariant")
            variant_value: Variant value to apply (e.g., "red")

        Returns:
            str: Path to the generated PNG thumbnail file

        Raises:
            CaptureException: If capture fails
        """
        if not HOU_AVAILABLE:
            raise CaptureException("Houdini is not available")

        if not self.variant_node:
            raise CaptureException("Viewport capture service not properly initialized")

        try:
            # Configure the setvariant node with the desired variant
            success = configure_set_variant_node(
                self.variant_node,
                prim_path,
                variant_set_name,
                variant_value
            )

            if not success:
                raise CaptureException("Failed to configure setvariant node")

            # Set the variant node as the display node so it updates the stage
            self.variant_node.setDisplayFlag(True)

            # Get the current scene viewer from the desktop
            desktop = hou.ui.curDesktop()
            scene_viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)

            if not scene_viewer:
                raise CaptureException("No scene viewer found in current desktop")

            # Get the viewport's actual aspect ratio
            viewport = scene_viewer.curViewport()
            viewport_aspect_ratio = viewport.settings().viewAspectRatio()

            # Calculate thumbnail resolution matching viewport aspect ratio
            thumb_width = self.THUMBNAIL_RESOLUTION[0]
            thumb_height = int(thumb_width / viewport_aspect_ratio)
            actual_resolution = (thumb_width, thumb_height)

            # Generate unique temp filename
            temp_filename = f"thumb_{hash(f'{prim_path}|{variant_set_name}|{variant_value}')}.png"
            temp_path = os.path.join(self.temp_directory, temp_filename)

            # Capture thumbnail using husd.assetutils from the main viewport
            assetutils.saveThumbnailFromViewer(
                sceneviewer=scene_viewer,
                frame=hou.frame(),
                res=actual_resolution,
                output=temp_path
            )

            # Verify file was created
            if not os.path.exists(temp_path):
                raise CaptureException(f"Thumbnail file not created: {temp_path}")

            return temp_path

        except CaptureException:
            raise
        except Exception as e:
            raise CaptureException(f"Capture failed: {str(e)}")

    def cleanup(self):
        """Clean up resources (node, temp files)."""
        try:
            # Delete setvariant node
            if self.variant_node:
                try:
                    self.variant_node.destroy()
                except:
                    pass
                self.variant_node = None

            # Clean up temp directory
            if self.temp_directory and os.path.exists(self.temp_directory):
                try:
                    import shutil
                    shutil.rmtree(self.temp_directory, ignore_errors=True)
                except:
                    pass
                self.temp_directory = None

        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

    def __del__(self):
        """Destructor - ensure cleanup happens."""
        self.cleanup()
