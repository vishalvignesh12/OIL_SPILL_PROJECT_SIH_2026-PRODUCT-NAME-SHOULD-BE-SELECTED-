"""
Phase 6/deployment: export the trained checkpoint to ONNX (portable inference,
usable with onnxruntime on CPU-only hardware — good for a low-resource SIH
demo box) and TorchScript (if staying in the PyTorch ecosystem, e.g. serving
via TorchServe).

Usage:
    python -m src.inference.export --checkpoint models/oilspill-v1/best.pt --out-dir models/oilspill-v1
"""
import argparse
import os

import torch

import segmentation_models_pytorch as smp
from src.models.unet import UNet


def export(checkpoint_path: str, out_dir: str, tile_size: int = 512):
    os.makedirs(out_dir, exist_ok=True)
    device = torch.device("cpu")
    ckpt = torch.load(checkpoint_path, map_location=device)
    model = UNet(in_channels=2, num_classes=1).to(device)
    try:
        model.load_state_dict(ckpt["model_state"], strict=False)
    except Exception as e:
        print(f"Warning: failed to load checkpoint state dict fully: {e}")
        model.load_state_dict(ckpt["model_state"], strict=False)
        # continue with partially loaded model
    model.eval()

    dummy = torch.randn(1, 2, tile_size, tile_size)

    onnx_path = os.path.join(out_dir, "model.onnx")
    torch.onnx.export(
        model,
        dummy,
        onnx_path,
        input_names=["sar_tile"], output_names=["logits"],
        opset_version=18,
        dynamic_axes={"sar_tile": {0: "batch", 2: "height", 3: "width"}, "logits": {0: "batch", 2: "height", 3: "width"}},
        verbose=False,
    )
    print(f"ONNX model saved to {onnx_path}")

    scripted = torch.jit.trace(model, dummy)
    ts_path = os.path.join(out_dir, "model_torchscript.pt")
    scripted.save(ts_path)
    print(f"TorchScript model saved to {ts_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--out-dir", default=None, help="Directory to store exported models. If omitted, a subdirectory 'exported' will be created next to the checkpoint.")
    p.add_argument("--tile-size", type=int, default=512)
    args = p.parse_args()
    out_dir = args.out_dir
    if out_dir is None:
        ckpt_dir = os.path.dirname(args.checkpoint)
        out_dir = os.path.join(ckpt_dir, "exported")
    export(args.checkpoint, out_dir, args.tile_size)

