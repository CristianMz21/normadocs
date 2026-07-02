"""Tests for ``normadocs.ocr``.

These tests do NOT require Tesseract on the CI path; they exercise
the preprocessing + pure functions directly via mocking. The
end-to-end ``extract_text_from_image`` test is marked
``@pytest.mark.ocr`` and only runs when ``tesseract`` is on PATH.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from normadocs.ocr import (
    OCRError,
    _preprocess,
    _resize_to_target,
    extract_text_from_image,
)


# ----------------------------------------------------------------------------
# Pure functions (no Tesseract dependency)
# ----------------------------------------------------------------------------


def test_resize_to_target_keeps_aspect_when_already_target() -> None:
    """An image already at the target width is returned unchanged."""
    img = np.zeros((100, 1500, 3), dtype=np.uint8)
    out = _resize_to_target(img, 1500)
    assert out.shape == img.shape


def test_resize_to_target_scales_height_proportionally() -> None:
    """Doubling the width doubles the height (aspect preserved)."""
    img = np.zeros((100, 800, 3), dtype=np.uint8)
    out = _resize_to_target(img, 1600)
    assert out.shape == (200, 1600, 3)


def test_preprocess_returns_grayscale_uint8() -> None:
    """Preprocessing outputs a 2D uint8 array (grayscale + threshold)."""
    img = np.full((300, 1500, 3), 128, dtype=np.uint8)
    out = _preprocess(img)
    assert out.ndim == 2
    assert out.dtype == np.uint8
    assert out.shape == (300, 1500)


# ----------------------------------------------------------------------------
# extract_text_from_image — mocked
# ----------------------------------------------------------------------------


def test_extract_text_returns_stripped_output(tmp_path: Path) -> None:
    """Successful extraction returns the engine output, stripped."""
    fake_path = tmp_path / "image.png"
    fake_path.write_bytes(b"\x89PNG\r\n\x1a\n")  # header only; OCR mocked

    with patch("normadocs.ocr._load_image") as mock_load, \
         patch("normadocs.ocr._preprocess") as mock_pre, \
         patch("normadocs.ocr.pytesseract.image_to_string") as mock_engine:
        mock_load.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_pre.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_engine.return_value = "  Hola mundo  \n"

        result = extract_text_from_image(fake_path)

    assert result == "Hola mundo"
    mock_load.assert_called_once()
    mock_pre.assert_called_once()
    mock_engine.assert_called_once()


def test_extract_text_raises_when_tesseract_missing(tmp_path: Path) -> None:
    """A TesseractNotFoundError is wrapped in OCRError with guidance."""
    fake_path = tmp_path / "image.png"
    fake_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    import pytesseract

    with patch("normadocs.ocr._load_image") as mock_load, \
         patch("normadocs.ocr._preprocess") as mock_pre:
        mock_load.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_pre.return_value = np.zeros((100, 100), dtype=np.uint8)
        with patch(
            "normadocs.ocr.pytesseract.image_to_string",
            side_effect=pytesseract.TesseractNotFoundError(),
        ):
            with pytest.raises(OCRError, match="tesseract binary not found"):
                extract_text_from_image(fake_path)


def test_extract_text_raises_when_engine_returns_empty(tmp_path: Path) -> None:
    """An empty engine output is surfaced as OCRError (no silent success)."""
    fake_path = tmp_path / "image.png"
    fake_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    with patch("normadocs.ocr._load_image") as mock_load, \
         patch("normadocs.ocr._preprocess") as mock_pre, \
         patch("normadocs.ocr.pytesseract.image_to_string") as mock_engine:
        mock_load.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_pre.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_engine.return_value = "   \n  \n"

        with pytest.raises(OCRError, match="OCR returned no text"):
            extract_text_from_image(fake_path)


def test_extract_text_raises_when_image_missing(tmp_path: Path) -> None:
    """A non-existent image path raises OCRError, not FileNotFoundError."""
    with pytest.raises(OCRError, match="image file not found"):
        extract_text_from_image(tmp_path / "does-not-exist.png")


# ----------------------------------------------------------------------------
# End-to-end (only when Tesseract is installed)
# ----------------------------------------------------------------------------


@pytest.mark.ocr
def test_extract_text_end_to_end_with_real_tesseract(tmp_path: Path) -> None:
    """End-to-end smoke: write a small image, run the pipeline."""
    import cv2

    img = np.full((400, 1500, 3), 255, dtype=np.uint8)
    cv2.putText(
        img,
        "Hola mundo",
        (50, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (0, 0, 0),
        5,
    )
    image_path = tmp_path / "sample.png"
    cv2.imwrite(str(image_path), img)

    text = extract_text_from_image(image_path)
    assert "hola" in text.lower() or "mundo" in text.lower()