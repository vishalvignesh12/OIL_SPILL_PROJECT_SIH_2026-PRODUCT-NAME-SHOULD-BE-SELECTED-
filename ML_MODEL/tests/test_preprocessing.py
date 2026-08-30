import numpy as np

from src.preprocessing.normalize import normalize_sar
from src.preprocessing.tiling import make_tiles, stitch_predictions


def test_normalize_sar_range():
    img = np.random.uniform(-40, 10, size=(2, 64, 64)).astype(np.float32)
    out = normalize_sar(img)
    assert out.shape == img.shape
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_make_tiles_covers_full_image():
    img = np.random.rand(2, 300, 300).astype(np.float32)
    tiles, offsets = make_tiles(img, tile_size=128, overlap=32)
    assert len(tiles) == len(offsets)
    for t in tiles:
        assert t.shape == (2, 128, 128)


def test_stitch_predictions_reconstructs_shape():
    h, w = 300, 300
    dummy = np.zeros((2, h, w), dtype=np.float32)
    tiles, offsets = make_tiles(dummy, tile_size=128, overlap=32)
    preds = [np.ones((128, 128), dtype=np.float32) * i for i, _ in enumerate(tiles)]
    stitched = stitch_predictions(preds, offsets, (h, w), tile_size=128)
    assert stitched.shape == (h, w)
