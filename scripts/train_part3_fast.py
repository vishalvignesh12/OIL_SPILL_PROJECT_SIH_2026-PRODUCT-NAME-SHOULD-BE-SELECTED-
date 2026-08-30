#!/usr/bin/env python
"""
Fast training script that trains only on Part 3 scenes.
It reuses the existing training utilities but filters the dataset to `part3` before the train/validation split.

Example usage:
    python -m scripts.train_part3_fast \
        --data-root data/raw \
        --out-dir models/oilspill-part3_fast \
        --epochs 5 \
        --fast-mode \
        --batch-size 8 \
        --tiles-per-scene-cap 4 \
        --max-train-scenes 500
"""

from __future__ import annotations
import argparse, os, json, time
import torch
from torch.utils.data import DataLoader

from src.models.unet import UNet
from src.preprocessing.dataset import OilSpillTileDataset
from src.preprocessing.loader import build_dataset_index, official_train_val_split
from src.training.losses import BCEDiceLoss
from src.training.metrics import aggregate_epoch_metrics, pixel_metrics


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default="data/raw")
    p.add_argument("--out-dir", default="models/oilspill-part3_fast")
    p.add_argument("--tile-size", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--lr", type=float, default=5e-4)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--bce-weight", type=float, default=0.3)
    p.add_argument("--pos-weight", type=float, default=5.0)
    p.add_argument("--fast-mode", action="store_true")
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--device", default=("cuda" if torch.cuda.is_available() else "cpu"))
    p.add_argument("--tiles-per-scene-cap", type=int, default=4)
    p.add_argument("--max-train-scenes", type=int, default=500)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device(args.device)
    print(f"Device: {device} | Tile size: {args.tile_size} | Batch size: {args.batch_size}")

    # Load full index then keep only part3 samples
    all_samples = build_dataset_index(args.data_root)
    samples = [s for s in all_samples if s.part == "part3"]
    if not samples:
        raise SystemExit("No part3 samples found – check your data layout.")

    # Manual 80/20 train/val split (shuffled)
    import random
    random.shuffle(samples)
    split_idx = int(0.8 * len(samples))
    train_s = samples[:split_idx]
    val_s = samples[split_idx:]
    if args.max_train_scenes and len(train_s) > args.max_train_scenes:
        train_s = train_s[: args.max_train_scenes]
        # Keep a proportionate number of validation scenes (at least 1)
        val_s = val_s[: max(1, args.max_train_scenes // 5)]
    print(f"[quick] Using {len(train_s)} train scenes and {len(val_s)} val scenes (part3)")

    if args.fast_mode:
        args.tile_size = 256
        print(f"[fast-mode] Reduced tile size to {args.tile_size}")

    train_ds = OilSpillTileDataset(train_s, tile_size=args.tile_size, train=True, tiles_per_scene_cap=args.tiles_per_scene_cap)
    val_ds   = OilSpillTileDataset(val_s,   tile_size=args.tile_size, train=False, tiles_per_scene_cap=args.tiles_per_scene_cap)

    use_pin = device.type == "cuda"
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.num_workers, pin_memory=use_pin, drop_last=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False,
                              num_workers=args.num_workers, pin_memory=use_pin)

    print(f"Dataset ready: {len(train_ds)} train tiles ({len(train_loader)} batches), {len(val_ds)} val tiles ({len(val_loader)} batches)")

    model = UNet(in_channels=2, num_classes=1).to(device) if args.fast_mode else UNet(in_channels=2, num_classes=1).to(device)
    criterion = BCEDiceLoss(bce_weight=args.bce_weight, pos_weight=args.pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=3)

    best_iou, epochs_without_improvement = -1.0, 0
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        print(f"\n--- Epoch {epoch}/{args.epochs} ---", flush=True)
        # Train
        train_loss, train_metrics = run_epoch(model, train_loader, criterion, device, optimizer)
        # Validate
        val_loss, val_metrics = run_epoch(model, val_loader, criterion, device, optimizer=None)
        scheduler.step(val_metrics["iou"])
        elapsed = time.time() - t0
        print(
            f"[epoch {epoch:03d}] {elapsed:.0f}s train_loss={train_loss:.4f} val_loss={val_loss:.4f} "
            f"val_iou={val_metrics['iou']:.4f} val_dice={val_metrics['dice']:.4f} "
            f"val_precision={val_metrics['precision']:.4f} val_recall={val_metrics['recall']:.4f} "
            f"lr={optimizer.param_groups[0]['lr']:.2e}",
            flush=True,
        )
        if val_metrics["iou"] > best_iou:
            best_iou = val_metrics["iou"]
            epochs_without_improvement = 0
            torch.save({"model_state": model.state_dict(), "epoch": epoch, "val_metrics": val_metrics, "config": vars(args)},
                       os.path.join(args.out_dir, "best.pt"))
            with open(os.path.join(args.out_dir, "metrics.json"), "w") as f:
                json.dump(val_metrics, f, indent=2)
            print(f"  -> new best (val_iou={best_iou:.4f}), checkpoint saved")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"Early stopping: no improvement for {args.patience} epochs")
                break

    # (Optional) save history / config – omitted for brevity


def run_epoch(model, loader, criterion, device, optimizer=None):
    train_mode = optimizer is not None
    model.train(train_mode)
    epoch_loss, batch_metrics = 0.0, []
    for images, masks in loader:
        images, masks = images.to(device), masks.to(device)
        with torch.set_grad_enabled(train_mode):
            logits = model(images)
            loss = criterion(logits, masks)
            if train_mode:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        epoch_loss += loss.item() * images.size(0)
        batch_metrics.append(pixel_metrics(logits.detach(), masks.detach()))
    avg_loss = epoch_loss / len(loader.dataset)
    metrics = aggregate_epoch_metrics(batch_metrics)
    return avg_loss, metrics


if __name__ == "__main__":
    main()
