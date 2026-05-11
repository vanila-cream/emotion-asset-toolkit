"""
ComfyUI Custom Node Package: Cream Saver 🎭

Saves images with a user-defined workflow template (Sampler_workflow.json),
injecting runtime values from RGTHREE_CONTEXT into the PNG metadata.

When the saved image is dragged back into ComfyUI, it loads the template
workflow with the correct per-image settings (prompt, seed, model, etc.).
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
