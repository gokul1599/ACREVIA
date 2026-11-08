"""
KisanVision - Image Reader & Binary Validator.
Handles format detection, cryptographic hashing, perceptual hashing, and corruption screening.
"""

import hashlib
import io
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


def compute_sha256(byte_data: bytes) -> str:
    """Compute SHA-256 digest of raw image bytes."""
    return hashlib.sha256(byte_data).hexdigest()


def compute_difference_hash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Compute perceptual difference hash (dHash) using PIL.
    Fast, deterministic, and invariant to minor compression artifacts.
    """
    # Resize to (hash_size + 1, hash_size) and convert to greyscale
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    if hasattr(resized, "get_flattened_data"):
        pixels = list(resized.get_flattened_data())
    else:
        pixels = list(resized.getdata())
    
    # Compare adjacent pixels horizontally
    diff = []
    width = hash_size + 1
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * width + col]
            right = pixels[row * width + col + 1]
            diff.append(left > right)
            
    # Convert binary array to hex string
    decimal_val = 0
    hex_str = []
    for index, value in enumerate(diff):
        if value:
            decimal_val += 2 ** (index % 4)
        if (index % 4) == 3:
            hex_str.append(f"{decimal_val:x}")
            decimal_val = 0
    return "".join(hex_str)


class ImageReadResult:
    def __init__(
        self,
        is_valid: bool,
        image: Optional[Image.Image] = None,
        sha256_hash: Optional[str] = None,
        phash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.image = image
        self.sha256_hash = sha256_hash
        self.phash = phash
        self.metadata = metadata or {}
        self.error_message = error_message


class ImageReader:
    """
    Safe image ingestion worker with format restriction and corruption screening.
    """
    @staticmethod
    def read_from_path(file_path: Path) -> ImageReadResult:
        if not file_path.exists():
            return ImageReadResult(is_valid=False, error_message=f"File not found: {file_path}")
            
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
            return ImageReader.read_from_bytes(raw_bytes, file_name=file_path.name)
        except Exception as e:
            return ImageReadResult(is_valid=False, error_message=f"Disk I/O error: {str(e)}")

    @staticmethod
    def read_from_bytes(raw_bytes: bytes, file_name: str = "memory_buffer") -> ImageReadResult:
        if not raw_bytes or len(raw_bytes) < 32:
            return ImageReadResult(is_valid=False, error_message="Empty or truncated byte stream")
            
        sha256_hash = compute_sha256(raw_bytes)
        
        try:
            # Verify image header and integrity without decoding full raster
            with Image.open(io.BytesIO(raw_bytes)) as probe_img:
                image_format = probe_img.format
                if image_format not in SUPPORTED_FORMATS:
                    return ImageReadResult(
                        is_valid=False,
                        sha256_hash=sha256_hash,
                        error_message=f"Unsupported format '{image_format}'. Allowed: {SUPPORTED_FORMATS}"
                    )
                probe_img.verify()

            # Fully decode the image into memory and handle orientation
            with Image.open(io.BytesIO(raw_bytes)) as decoded_img:
                # Handle EXIF orientation tags cleanly
                oriented_img = ImageOps.exif_transpose(decoded_img)
                # Ensure conversion to standard RGB (drops alpha / palette modes)
                rgb_img = oriented_img.convert("RGB")
                phash_val = compute_difference_hash(rgb_img)
                
                metadata = {
                    "original_filename": file_name,
                    "format": image_format,
                    "width": rgb_img.width,
                    "height": rgb_img.height,
                    "aspect_ratio": round(rgb_img.width / max(rgb_img.height, 1), 3),
                    "file_size_bytes": len(raw_bytes)
                }
                
                return ImageReadResult(
                    is_valid=True,
                    image=rgb_img,
                    sha256_hash=sha256_hash,
                    phash=phash_val,
                    metadata=metadata
                )

        except (UnidentifiedImageError, OSError, SyntaxError) as e:
            return ImageReadResult(
                is_valid=False,
                sha256_hash=sha256_hash,
                error_message=f"Corrupt or unreadable image stream: {str(e)}"
            )
        except Exception as e:
            return ImageReadResult(
                is_valid=False,
                sha256_hash=sha256_hash,
                error_message=f"Unexpected decode failure: {str(e)}"
            )
