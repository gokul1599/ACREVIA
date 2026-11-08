"""
KisanVision Inference Service - Defensive Image Ingestion Validator.
Enforces strict size limits, MIME magic byte verification, and decompression bomb protection.
"""

import io
from pathlib import Path
from typing import Tuple
from PIL import Image

from ml.inference_service.app.core.config import config

# Protect host from image decompression bombs
Image.MAX_IMAGE_PIXELS = 25_000_000


class ImageIngestionValidator:
    """
    Defensive input sanitizer for binary image payloads.
    """
    @staticmethod
    def validate_magic_bytes(data: bytes) -> str:
        """
        Inspects binary file signature to verify true MIME type independent of client claims.
        """
        if len(data) < 12:
            raise ValueError("File payload too small to be a valid image.")

        # JPEG signature: 0xFF, 0xD8, 0xFF
        if data[:3] == b"\xff\xd8\xff":
            return "image/jpeg"
        # PNG signature: 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A
        elif data[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        # WebP signature: RIFF....WEBP
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return "image/webp"
        else:
            raise ValueError("Unsupported or disguised image format. Allowed formats: JPEG, PNG, WebP.")

    @classmethod
    def validate_and_decode(
        cls,
        image_bytes: bytes,
        filename: str = "upload.jpg"
    ) -> Tuple[Image.Image, str]:
        """
        Performs end-to-end defensive validation and returns (PIL.Image, mime_type).
        """
        # 1. Size bounds check
        byte_len = len(image_bytes)
        if byte_len == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")
        if byte_len > config.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size ({round(byte_len / (1024 * 1024), 2)} MB) exceeds "
                f"maximum allowed limit of {config.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        # 2. Magic byte check
        detected_mime = cls.validate_magic_bytes(image_bytes)
        if detected_mime not in config.ALLOWED_MIME_TYPES:
            raise ValueError(f"MIME type '{detected_mime}' is not permitted.")

        # 3. Extension check
        ext = Path(filename).suffix.lower()
        if ext and ext not in config.ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension '{ext}' does not match allowed types: {config.ALLOWED_EXTENSIONS}")

        # 4. Safe image decoding
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.load()  # Force reading compressed pixel buffers
        except Exception as e:
            raise ValueError(f"Image decompression failed: corrupted or truncated image data ({str(e)})")

        return image, detected_mime
