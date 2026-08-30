"""
DeepLabv3+ (PRD §13 Option B, RECOMMENDED comparison against the U-Net
baseline). Uses torchvision's ResNet50-backboned DeepLabv3 and swaps the
first conv to accept 2 channels (VV, VH) and the classifier head to 1
output channel (binary oil/not-oil logit).

Only build/compare this after the U-Net baseline is measured (PRD §52) —
don't reach for it first just because it's bigger.
"""
import torch
import torch.nn as nn
from torchvision.models.segmentation import deeplabv3_resnet50


def build_deeplab(in_channels: int = 2, num_classes: int = 1, pretrained_backbone: bool = True) -> nn.Module:
    model = deeplabv3_resnet50(weights=None, weights_backbone="DEFAULT" if pretrained_backbone else None)

    # Swap first conv: pretrained weights are for 3-channel RGB ImageNet input.
    # Average the 3 pretrained input-channel kernels down to init 2 new ones
    # rather than random-initializing from scratch.
    old_conv = model.backbone.conv1
    new_conv = nn.Conv2d(in_channels, old_conv.out_channels, kernel_size=old_conv.kernel_size,
                          stride=old_conv.stride, padding=old_conv.padding, bias=False)
    if pretrained_backbone:
        with torch.no_grad():
            avg_kernel = old_conv.weight.mean(dim=1, keepdim=True)  # (out, 1, k, k)
            new_conv.weight.copy_(avg_kernel.repeat(1, in_channels, 1, 1))
    model.backbone.conv1 = new_conv

    # Swap classifier head to num_classes output channels
    model.classifier[4] = nn.Conv2d(256, num_classes, kernel_size=1)
    if model.aux_classifier is not None:
        model.aux_classifier[4] = nn.Conv2d(256, num_classes, kernel_size=1)

    return model


if __name__ == "__main__":
    m = build_deeplab(pretrained_backbone=False)
    x = torch.randn(2, 2, 512, 512)
    y = m(x)["out"]
    print("output shape:", y.shape)
    print("params (M):", sum(p.numel() for p in m.parameters()) / 1e6)
