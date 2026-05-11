"""
Cream Saver - ComfyUI Custom Node
Saves images with a custom workflow template, injecting RGTHREE_CONTEXT values
so that drag-and-drop restores a per-emotion editing workflow.
"""

import os
import json
import copy
import numpy as np
from PIL import Image

import folder_paths
import comfy.samplers
from comfy.cli_args import args


class SaveImageWithContext:
    """Saves an image with a custom workflow (Sampler_workflow.json),
    replacing template placeholders with actual values from RGTHREE_CONTEXT."""

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

        # Load template workflow from the same directory as this file
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Sampler_workflow.json"
        )
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template_workflow = json.load(f)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "context": ("RGTHREE_CONTEXT",),
                "filename_prefix": ("STRING", {"default": "emotion"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    @staticmethod
    def _to_python(value):
        """Convert tensor scalars to plain Python types for JSON serialization."""
        if value is None:
            return None
        if hasattr(value, 'item'):
            return value.item()
        return value

    def _build_workflow(self, context, saved_filename=None,
                        image_width=None, image_height=None):
        """Deep-copy the template workflow and inject context values."""
        workflow = copy.deepcopy(self.template_workflow)

        # Extract values from RGTHREE_CONTEXT dict
        text_pos_g = context.get("text_pos_g") or ""
        text_neg_g = context.get("text_neg_g") or ""
        ckpt_name  = context.get("ckpt_name") or ""
        seed       = self._to_python(context.get("seed"))
        steps      = self._to_python(context.get("steps"))
        cfg        = self._to_python(context.get("cfg"))
        sampler    = context.get("sampler") or ""
        scheduler  = context.get("scheduler") or ""
        lora_stack = context.get("lora_stack")

        # Build a quick lookup by node id
        node_map = {n["id"]: n for n in workflow["nodes"]}

        # ── Node 19: Get Booru Tag 💬ED (positive prompt) ──
        if 19 in node_map:
            node_map[19]["widgets_values"][1] = text_pos_g

        # ── Node 18: Simple Text (negative prompt) ──
        if 18 in node_map:
            node_map[18]["widgets_values"][0] = text_neg_g

        # ── Node 5: Efficient Loader 💬ED ──
        # widgets_values order:
        #   [0] ckpt_name  [1] vae_name  [2] clip_skip
        #   [3] paint_mode [4] batch_size [5] seed
        #   [6] (control)  [7] cfg  [8] sampler  [9] scheduler
        #   [10] width  [11] height
        if 5 in node_map:
            wv = node_map[5]["widgets_values"]
            if ckpt_name:
                wv[0] = ckpt_name
            if seed is not None:
                wv[5] = seed
            if cfg is not None:
                wv[7] = cfg
            if sampler:
                wv[8] = sampler
            if scheduler:
                wv[9] = scheduler
            if image_width is not None:
                wv[10] = image_width
            if image_height is not None:
                wv[11] = image_height

        # ── Node 4: KSampler (Efficient) 💬ED ──
        # widgets_values order:
        #   [0] set_seed_cfg_sampler  [1] seed  [2] control_after_generate
        #   [3] steps  [4] cfg  [5] sampler  [6] scheduler
        #   [7] denoise  [8..13] guide_size etc.
        if 4 in node_map:
            wv = node_map[4]["widgets_values"]
            if seed is not None:
                wv[1] = seed
            if steps is not None:
                wv[3] = steps
            if cfg is not None:
                wv[4] = cfg
            if sampler:
                wv[5] = sampler
            if scheduler:
                wv[6] = scheduler

        # ── Node 6: Int Holder 💬ED (Steps) ──
        if 6 in node_map and steps is not None:
            node_map[6]["widgets_values"][0] = steps

        # ── Node 16: LoRA Stacker 💬ED ──
        # widgets_values layout (simple mode):
        #   [0] input_mode  [1] lora_count
        #   For each LoRA slot i (0..8):
        #     [2 + i*4] lora_name   [3 + i*4] lora_wt
        #     [4 + i*4] model_str   [5 + i*4] clip_str
        #   [38..46] toggles for slots 1..9
        #   [47] "Clear LoRAs"
        if 16 in node_map and lora_stack is not None and len(lora_stack) > 0:
            wv = node_map[16]["widgets_values"]
            num_loras = min(len(lora_stack), 9)
            wv[1] = num_loras  # lora_count
            for i in range(9):
                base = 2 + i * 4
                if i < num_loras:
                    name, model_w, clip_w = lora_stack[i]
                    wv[base]     = name
                    wv[base + 1] = model_w  # lora_wt (simple mode weight)
                    wv[base + 2] = 1        # model_str (unused in simple mode)
                    wv[base + 3] = 1        # clip_str  (unused in simple mode)
                else:
                    # Clear unused slots
                    wv[base]     = "None"
                    wv[base + 1] = 1
                    wv[base + 2] = 1
                    wv[base + 3] = 1

        # ── Node 2: Load Image 💬ED (saved filename) ──
        # Set the image widget to the saved filename so drag-and-drop
        # auto-references the correct image in ComfyUI's input directory.
        if 2 in node_map and saved_filename is not None:
            node_map[2]["widgets_values"][0] = saved_filename

        return workflow

    def save_images(self, images, context, filename_prefix="emotion",
                    prompt=None, extra_pnginfo=None):
        """Save each image in the batch with customized workflow metadata."""

        # Resolve output path (ComfyUI standard helper)
        full_output_folder, filename, counter, subfolder, filename_prefix = \
            folder_paths.get_save_image_path(
                filename_prefix, self.output_dir,
                images[0].shape[1], images[0].shape[0]
            )

        results = []
        for batch_idx, image_tensor in enumerate(images):
            # Determine filename first (needed for workflow injection)
            file = f"{filename}_{counter:05}_.webp"

            # Build the per-emotion workflow with this image's filename
            # Image tensor shape: (height, width, channels)
            img_h = image_tensor.shape[0]
            img_w = image_tensor.shape[1]

            custom_workflow = self._build_workflow(
                context,
                saved_filename=file,
                image_width=img_w,
                image_height=img_h,
            )

            # Tensor → PIL Image
            arr = 255.0 * image_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

            # Build EXIF metadata using ComfyUI's WebP convention
            # so the frontend's getWebpMetadata can restore the workflow
            # on drag-and-drop.
            exif_bytes = b""
            if not args.disable_metadata:
                exif = Image.Exif()
                # 0x010f (Make) = workflow JSON for drag-and-drop restore
                exif[0x010f] = "workflow:" + json.dumps(custom_workflow)
                # 0x0110 (Model) = API prompt graph
                if prompt is not None:
                    exif[0x0110] = "prompt:" + json.dumps(prompt)
                exif_bytes = exif.tobytes()

            img.save(
                os.path.join(full_output_folder, file),
                format="WEBP",
                lossless=True,
                quality=100,
                method=4,
                exif=exif_bytes,
            )
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type,
            })
            counter += 1

        return {"ui": {"images": results}}


class ContextCream:
    """Like Context Big (rgthree) but with LORA_STACK support.
    Accepts a base RGTHREE_CONTEXT, allows overriding any field,
    and passes LORA_STACK alongside the context.

    Derived from rgthree-comfy's Context Big node
    (https://github.com/rgthree/rgthree-comfy, MIT © 2023 rgthree).
    """

    # Ordered list of context field keys (must match RETURN order)
    _CTX_KEYS = [
        "model", "clip", "vae", "positive", "negative",
        "latent", "images", "seed", "steps", "step_refiner", "cfg",
        "ckpt_name", "sampler", "scheduler",
        "clip_width", "clip_height",
        "text_pos_g", "text_pos_l", "text_neg_g", "text_neg_l",
        "mask", "control_net",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "base_ctx":     ("RGTHREE_CONTEXT",),
                "model":        ("MODEL",),
                "clip":         ("CLIP",),
                "vae":          ("VAE",),
                "positive":     ("CONDITIONING",),
                "negative":     ("CONDITIONING",),
                "latent":       ("LATENT",),
                "images":       ("IMAGE",),
                "seed":         ("INT",   {"forceInput": True}),
                "steps":        ("INT",   {"forceInput": True}),
                "step_refiner": ("INT",   {"forceInput": True}),
                "cfg":          ("FLOAT", {"forceInput": True}),
                "ckpt_name":    (folder_paths.get_filename_list("checkpoints"),
                                 {"forceInput": True}),
                "sampler":      (comfy.samplers.KSampler.SAMPLERS,
                                 {"forceInput": True}),
                "scheduler":    (comfy.samplers.KSampler.SCHEDULERS,
                                 {"forceInput": True}),
                "clip_width":   ("INT",    {"forceInput": True}),
                "clip_height":  ("INT",    {"forceInput": True}),
                "text_pos_g":   ("STRING", {"forceInput": True}),
                "text_pos_l":   ("STRING", {"forceInput": True}),
                "text_neg_g":   ("STRING", {"forceInput": True}),
                "text_neg_l":   ("STRING", {"forceInput": True}),
                "mask":         ("MASK",),
                "control_net":  ("CONTROL_NET",),
                "lora_stack":   ("LORA_STACK",),
            },
        }

    RETURN_TYPES = (
        "RGTHREE_CONTEXT", "LORA_STACK",
        "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING",
        "LATENT", "IMAGE", "INT", "INT", "INT", "FLOAT",
        folder_paths.get_filename_list("checkpoints"),
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS,
        "INT", "INT", "STRING", "STRING", "STRING", "STRING",
        "MASK", "CONTROL_NET",
    )
    RETURN_NAMES = (
        "CONTEXT", "LORA_STACK",
        "MODEL", "CLIP", "VAE", "POSITIVE", "NEGATIVE",
        "LATENT", "IMAGE", "SEED", "STEPS", "STEP_REFINER", "CFG",
        "CKPT_NAME", "SAMPLER", "SCHEDULER",
        "CLIP_WIDTH", "CLIP_HEIGHT",
        "TEXT_POS_G", "TEXT_POS_L", "TEXT_NEG_G", "TEXT_NEG_L",
        "MASK", "CONTROL_NET",
    )
    FUNCTION = "build_context"
    CATEGORY = "context"

    def build_context(self, base_ctx=None, lora_stack=None, **kwargs):
        """Build or modify an RGTHREE_CONTEXT, passing LORA_STACK alongside."""
        ctx = {}
        for key in self._CTX_KEYS:
            new_val  = kwargs.get(key)
            base_val = (base_ctx.get(key)
                        if base_ctx is not None and key in base_ctx
                        else None)
            ctx[key] = new_val if new_val is not None else base_val

        # Embed lora_stack inside the context so downstream nodes
        # (e.g. Cream Image Save) can read it without a separate input.
        # Falls back to base_ctx's lora_stack if not provided here.
        if lora_stack is None and base_ctx is not None:
            lora_stack = base_ctx.get("lora_stack")
        ctx["lora_stack"] = lora_stack

        # Output: (CONTEXT, LORA_STACK, field1, field2, ...)
        outputs = [ctx, lora_stack]
        for key in self._CTX_KEYS:
            outputs.append(ctx.get(key))
        return tuple(outputs)


# ─── Node Registration ───────────────────────────────────────────────
NODE_CLASS_MAPPINGS = {
    "SaveImageWithContext": SaveImageWithContext,
    "ContextCream": ContextCream,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithContext": "Cream Image Save with Context",
    "ContextCream": "Context Cream",
}
