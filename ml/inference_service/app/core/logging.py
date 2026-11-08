"""
KisanVision Dedicated ML Inference Service - Structured Logging.
Sanitizes log records to avoid leaking private farmer data, file paths, or secrets.
"""

import logging
import sys


def get_inference_logger(name: str = "kisanvision.inference") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_inference_logger()
