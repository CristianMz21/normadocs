"""OCR module — text extraction from images via Tesseract.

Provides a single public function: :func:`extract_text_from_image`.

The pipeline mirrors the standalone ``google_colab_ocr_preciso.py``
notebook that was previously used ad-hoc on Google Colab:

1. Load the image from disk (PNG/JPG/JPEG/BMP/TIFF).
2. Resize to a width of 1500 px (preserves aspect ratio) so Tesseract
   can extract dense text reliably.
3. Convert to grayscale.
4. Denoise with ``cv2.fastNlMeansDenoising``.
5. Apply adaptive Gaussian threshold (``cv2.adaptiveThreshold``) to
   clean up low-contrast backgrounds.
6. Run ``pytesseract.image_to_string`` with Spanish + English language
   packs (``spa+eng``).

Raises :class:`OCRError` on any failure (missing tesseract binary,
unreadable image, empty output).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image


class OCRError(RuntimeError):
    """Raised when the OCR pipeline cannot produce output."""


# Tesseract language packs. Spanish + English covers the common LATAM
# academic / professional use case.
_LANGS: str = "spa+eng"

# Resize target width. Below ~800 px Tesseract accuracy drops sharply
# for small body text; above ~2000 px the engine slows without gains.
_TARGET_WIDTH: int = 1500

# Fast non-local means denoising filter strength (matches the Colab
# notebook preset that produced clean output).
_DENOISE_H: int = 30


def _load_image(image_path: Path) -> np.ndarray:
    """Read an image file as a BGR numpy array."""
    if not image_path.is_file():
        raise OCRError(f"image file not found: {image_path}")
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise OCRError(f"could not decode image: {image_path}")
    return img


def _resize_to_target(img: np.ndarray, target_width: int) -> np.ndarray:
    """Resize ``img`` so its width is ``target_width`` (aspect preserved)."""
    height, width = img.shape[:2]
    if width == target_width:
        return img
    scale = target_width / float(width)
    new_height = int(round(height * scale))
    return cv2.resize(img, (target_width, new_height), interpolation=cv2.INTER_CUBIC)


def _preprocess(img_bgr: np.ndarray) -> np.ndarray:
    """Apply the OCR-friendly preprocessing pipeline.

    Steps (matches the standalone Colab script):

    1. BGR -> RGB (PIL compatibility).
    2. Resize to ``_TARGET_WIDTH``.
    3. Grayscale.
    4. ``cv2.fastNlMeansDenoising`` (strength ``_DENOISE_H``).
    5. Histogram equalisation.
    6. Adaptive Gaussian threshold.
    """
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    resized = _resize_to_target(img_rgb, _TARGET_WIDTH)
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, _DENOISE_H, 7, 21)
    equalised = cv2.equalizeHist(denoised)
    thresh = cv2.adaptiveThreshold(
        equalised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15,
    )
    return thresh


def extract_text_from_image(image_path: str | Path, *, lang: str = _LANGS) -> str:
    """Extract text from an image file using Tesseract.

    Args:
        image_path: Path to a PNG / JPG / JPEG / BMP / TIFF file.
        lang: Tesseract language packs (default ``"spa+eng"``).

    Returns:
        The extracted text, stripped of trailing whitespace.

    Raises:
        OCRError: If the image cannot be loaded, the Tesseract binary
            is not installed, or the engine returns no output.
    """
    path = Path(image_path)
    try:
        img_bgr = _load_image(path)
        processed = _preprocess(img_bgr)
        pil_image = Image.fromarray(processed)
        text = pytesseract.image_to_string(pil_image, lang=lang)
    except pytesseract.TesseractNotFoundError as exc:
        raise OCRError(
            "tesseract binary not found on PATH; install with "
            "`apt install tesseract-ocr tesseract-ocr-spa`"
        ) from exc
    except FileNotFoundError as exc:
        raise OCRError(f"image file not found: {path}") from exc
    if not text or not text.strip():
        raise OCRError(f"OCR returned no text for image: {path}")
    return text.strip()


__all__ = ["OCRError", "extract_text_from_image"]