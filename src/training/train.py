"""
Training loop for the U-Net baseline (PRD Phase 3).

Usage:
    python -m src.training.train --data-root data/raw --epochs 40 --batch-size 8
"""
from __future__ import annotations

import argparse
import json
import os
import time

import torch
import segmentation_models_pytorch as smp
from torch.utils.data import DataLoader

from src.models.unet import UNet
from src.preprocessing.dataset import OilSpillTileDataset
from src.preprocessing.loader import build_dataset_index, official_train_val_split
from src.training.losses import BCEDiceLoss
from src.training.metrics import aggregate_epoch_metrics, pixel_metrics


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default="data/raw")
    p.add_argument("--out-dir", default="models/oilspill-v1")
    p.add_argument("--tile-size", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--epochs", type=int, default=20, help="number of epochs (fast mode target)")
    p.add_argument("--lr", type=float, default=5e-4, help="learning rate")
    p.add_argument("--patience", type=int, default=10, help="early‑stopping patience (epochs)")
    p.add_argument("--bce-weight", type=float, default=0.3, help="weight for BCE loss (dice gets higher emphasis)")
    p.add_argument("--pos-weight", type=float, default=5.0, help="upweight the rarer oil‑foreground class in BCE")
    p.add_argument("--fast-mode", action="store_true", help="use lightweight UNet and smaller tiles for ultra‑fast epochs")
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--tiles-per-scene-cap", type=int, default=8,
                    help="max tiles sampled per scene during training (lower = faster, hackathon mode)")
    p.add_argument("--max-train-scenes", type=int, default=None,
                    help="cap total train scenes for lightning fast hackathon demo")
    return p.parse_args()


def run_epoch(model, loader, criterion, device, optimizer=None):
    train_mode = optimizer is not None
    model.train(train_mode)
    epoch_loss, batch_metrics = 0.0, []
    total_batches = len(loader)

    for batch_idx, (images, masks) in enumerate(loader):
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
        
        if (batch_idx + 1) % 10 == 0 or (batch_idx + 1) == total_batches:
            mode_str = "Train" if train_mode else "Val"
            print(f"  [{mode_str}] Batch {batch_idx+1}/{total_batches} - batch_loss: {loss.item():.4f}", flush=True)

    avg_loss = epoch_loss / len(loader.dataset)
    metrics = aggregate_epoch_metrics(batch_metrics)
    return avg_loss, metrics


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device(args.device)

    print(f"Device: {device} | Tile size: {args.tile_size} | Batch size: {args.batch_size}", flush=True)
    samples = build_dataset_index(args.data_root)
    train_s, val_s, _ = official_train_val_split(samples)
    if args.max_train_scenes and len(train_s) > args.max_train_scenes:
        train_s = train_s[:args.max_train_scenes]
        val_s = val_s[:max(20, args.max_train_scenes // 5)]
        print(f"[hackathon-fast] Capped to {len(train_s)} train scenes and {len(val_s)} val scenes", flush=True)

    if args.fast_mode:
        args.tile_size = 256
        print(f"[fast-mode] Reduced tile size to {args.tile_size}", flush=True)

    train_ds = OilSpillTileDataset(train_s, tile_size=args.tile_size, train=True,
                                    tiles_per_scene_cap=args.tiles_per_scene_cap)
    val_ds = OilSpillTileDataset(val_s, tile_size=args.tile_size, train=False,
                                  tiles_per_scene_cap=args.tiles_per_scene_cap)

    use_pin = (device.type == "cuda")
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                               num_workers=args.num_workers, pin_memory=use_pin, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                             num_workers=args.num_workers, pin_memory=use_pin)

    print(f"Dataset ready: {len(train_ds)} train tiles ({len(train_loader)} batches), {len(val_ds)} val tiles ({len(val_loader)} batches)", flush=True)

    if args.fast_mode:
        model = UNet(in_channels=2, num_classes=1).to(device)
    else:
        model = smp.Unet(encoder_name="resnet34", encoder_weights="imagenet", in_channels=2, classes=1).to(device)
    # Use BCE weight argument to give more emphasis to Dice
    criterion = BCEDiceLoss(bce_weight=args.bce_weight, pos_weight=args.pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    # Resume from existing checkpoint if present
    checkpoint_path = os.path.join(args.out_dir, "best.pt")
    start_epoch = 1
    if os.path.isfile(checkpoint_path):
        try:
            ckpt = torch.load(checkpoint_path, map_location=device)
            model.load_state_dict(ckpt["model_state"])
            start_epoch = ckpt.get("epoch", 0) + 1
            best_iou = ckpt.get("val_metrics", {}).get("iou", -1.0)
            print(f"Resuming from epoch {start_epoch-1}, best_iou={best_iou:.4f}", flush=True)
        except RuntimeError as e:
            print(f"[Warning] Failed to load checkpoint due to architecture mismatch: {e}", flush=True)
            print("Starting training from epoch 1", flush=True)
            start_epoch = 1
    else:
        start_epoch = 1
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=3
    )

    best_iou, epochs_without_improvement = -1.0, 0
    history = []

    for epoch in range(start_epoch, args.epochs + 1):
        t0 = time.time()
        # Enforce max epoch time of 90 seconds (1.5 minutes)
        max_epoch_seconds = 90
        print(f"\n--- Epoch {epoch}/{args.epochs} ---", flush=True)
        train_loss, train_metrics = run_epoch(model, train_loader, criterion, device, optimizer)
        val_loss, val_metrics = run_epoch(model, val_loader, criterion, device, optimizer=None)
        scheduler.step(val_metrics["iou"])

        elapsed = time.time() - t0
        print(f"[epoch {epoch:03d}] {elapsed:.0f}s "
              f"train_loss={train_loss:.4f} val_loss={val_loss:.4f} "
              f"val_iou={val_metrics['iou']:.4f} val_dice={val_metrics['dice']:.4f} "
              f"val_precision={val_metrics['precision']:.4f} val_recall={val_metrics['recall']:.4f} "
              f"lr={optimizer.param_groups[0]['lr']:.2e}", flush=True)
        if elapsed > max_epoch_seconds:
            print(f"[Warning] Epoch {epoch} exceeded 90s ({elapsed:.0f}s). Consider adjusting fast-mode parameters.", flush=True)

        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss, **val_metrics})

        if val_metrics["iou"] > best_iou:
            best_iou = val_metrics["iou"]
            epochs_without_improvement = 0
            torch.save({"model_state": model.state_dict(),
                        "epoch": epoch,
                        "val_metrics": val_metrics,
                        "config": vars(args)},
                       os.path.join(args.out_dir, "best.pt"))
            with open(os.path.join(args.out_dir, "metrics.json"), "w") as f:
                json.dump(val_metrics, f, indent=2)
            print(f"  -> new best (val_iou={best_iou:.4f}), checkpoint saved")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"Early stopping: no val_iou improvement in {args.patience} epochs")
                break

    with open(os.path.join(args.out_dir, "history.json"), "w") as f:
        json.dump(history, f, indent=2)
    with open(os.path.join(args.out_dir, "config.json"), "w") as f:
        json.dump(vars(args), f, indent=2)
    print(f"Training complete. Best val IoU={best_iou:.4f}. Artifacts in {args.out_dir}/")


if __name__ == "__main__":
    main()
