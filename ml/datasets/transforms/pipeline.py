"""
KisanVision - Image Preprocessing & Augmentation Pipelines.
Defines scientifically grounded transformations ensuring training vs inference consistency.
"""

from torchvision import transforms
from typing import Tuple


# Standard ImageNet normalization coefficients
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_training_transforms(image_size: Tuple[int, int] = (224, 224)) -> transforms.Compose:
    """
    Stochastic data augmentation designed specifically for agricultural foliage.
    Applies realistic field variations (rotations, mild lighting shifts) while
    preserving subtle necrotic lesions and vein structures.
    """
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(
            brightness=0.15,
            contrast=0.15,
            saturation=0.15,
            hue=0.05
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def get_validation_transforms(image_size: Tuple[int, int] = (224, 224)) -> transforms.Compose:
    """
    Deterministic evaluation transformation: standard resizing, tensor conversion, and normalization.
    Zero stochastic perturbations applied.
    """
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def get_inference_transforms(image_size: Tuple[int, int] = (224, 224)) -> transforms.Compose:
    """
    Inference transformation: must remain strictly identical to validation pipeline.
    """
    return get_validation_transforms(image_size=image_size)
