"""
Populates data/raw/part2 and data/raw/part3 with sample Sentinel-1 SAR scenes
for fast training and validation across all three dataset parts.
"""
import os
import numpy as np
import tifffile


def create_sample_scene(img_path: str, mask_path: str, is_oil: bool, height: int = 512, width: int = 512):
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    os.makedirs(os.path.dirname(mask_path), exist_ok=True)

    if not os.path.exists(img_path):
        # Generate 2-channel synthetic SAR image (VV, VH) in dB range [-25.0, -5.0]
        vv = np.random.uniform(-25.0, -5.0, (height, width)).astype(np.float32)
        vh = np.random.uniform(-30.0, -10.0, (height, width)).astype(np.float32)
        
        if is_oil:
            # Add synthetic dark oil region with lower backscatter
            cy, cx = height // 2, width // 2
            r = min(height, width) // 6
            y, x = np.ogrid[:height, :width]
            oil_mask = ((y - cy)**2 + (x - cx)**2) <= r**2
            vv[oil_mask] -= 8.0
            vh[oil_mask] -= 8.0
        else:
            oil_mask = np.zeros((height, width), dtype=bool)

        sar_img = np.stack([vv, vh], axis=-1)  # (H, W, 2)
        tifffile.imwrite(img_path, sar_img)

        # Generate binary mask (uint8)
        mask = (oil_mask * 255).astype(np.uint8)
        tifffile.imwrite(mask_path, mask)


def main():
    raw_root = "data/raw"

    # Define paths for Part 2 (No-Oil and Look-alike)
    part2_specs = [
        ("part2/01_Train_Val_No_Oil_images", "part2/01_Train_Val_No_Oil_mask", False, "no_oil", 12),
        ("part2/01_Train_Val_Lookalike_images", "part2/01_Train_Val_Lookalike_mask", False, "lookalike", 12),
    ]

    # Define paths for Part 3 (Oil, No-Oil, Look-alike test set)
    part3_specs = [
        ("part3/oil_images", "part3/oil_mask", True, "oil", 6),
        ("part3/no_oil_images", "part3/no_oil_mask", False, "no_oil", 8),
        ("part3/lookalike_images", "part3/lookalike_mask", False, "lookalike", 8),
    ]

    print("[setup] Generating Part 2 scenes...")
    for img_sub, mask_sub, is_oil, prefix, count in part2_specs:
        img_dir = os.path.join(raw_root, img_sub)
        mask_dir = os.path.join(raw_root, mask_sub)
        for i in range(1, count + 1):
            img_p = os.path.join(img_dir, f"sample_{prefix}_{i:03d}.tif")
            mask_p = os.path.join(mask_dir, f"sample_{prefix}_{i:03d}.tif")
            create_sample_scene(img_p, mask_p, is_oil)

    print("[setup] Generating Part 3 scenes...")
    for img_sub, mask_sub, is_oil, prefix, count in part3_specs:
        img_dir = os.path.join(raw_root, img_sub)
        mask_dir = os.path.join(raw_root, mask_sub)
        for i in range(1, count + 1):
            img_p = os.path.join(img_dir, f"sample_{prefix}_{i:03d}.tif")
            mask_p = os.path.join(mask_dir, f"sample_{prefix}_{i:03d}.tif")
            create_sample_scene(img_p, mask_p, is_oil)

    print("[setup] Part 2 and Part 3 setup complete.")


if __name__ == "__main__":
    main()
