"""
Utilities for inspecting the oil spill dataset.

This module helps us understand the dataset structure before
building the training pipeline.
"""

from pathlib import Path
from collections import Counter


SUPPORTED_IMAGE_EXTENSIONS = {
    ".tif",
    ".tiff",
    ".png",
    ".jpg",
    ".jpeg",
    ".npy",
}


def find_files(directory: Path) -> list[Path]:
    """
    Find all supported image/data files recursively.

    Args:
        directory: Root directory to inspect.

    Returns:
        List of matching file paths.
    """
    if not directory.exists():
        return []

    return sorted(
        file_path
        for file_path in directory.rglob("*")
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    )


def inspect_dataset(dataset_path: str | Path) -> dict:
    """
    Inspect the dataset and return basic file information.

    Args:
        dataset_path: Path to the dataset directory.

    Returns:
        Dictionary containing dataset statistics.
    """
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {dataset_path}"
        )

    files = find_files(dataset_path)

    extension_counts = Counter(
        file_path.suffix.lower()
        for file_path in files
    )

    return {
        "dataset_path": str(dataset_path.resolve()),
        "total_files": len(files),
        "extension_counts": dict(extension_counts),
        "sample_files": [
            str(file_path.relative_to(dataset_path))
            for file_path in files[:10]
        ],
    }


def print_dataset_info(dataset_path: str | Path) -> None:
    """
    Print a readable dataset summary.
    """
    info = inspect_dataset(dataset_path)

    print("\n=== OIL SPILL DATASET INSPECTION ===")
    print(f"Dataset path: {info['dataset_path']}")
    print(f"Total supported files: {info['total_files']}")

    print("\nFile types:")
    if info["extension_counts"]:
        for extension, count in sorted(
            info["extension_counts"].items()
        ):
            print(f"  {extension}: {count}")
    else:
        print("  No supported files found.")

    print("\nSample files:")
    if info["sample_files"]:
        for file_name in info["sample_files"]:
            print(f"  - {file_name}")
    else:
        print("  No files found.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect an oil spill dataset."
    )

    parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to the dataset directory.",
    )

    args = parser.parse_args()

    print_dataset_info(args.dataset_path)