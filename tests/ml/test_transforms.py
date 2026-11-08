"""
Tests for Image Transforms & Normalization Consistency.
"""

from PIL import Image
import torch
from ml.datasets.transforms.pipeline import (
    get_training_transforms,
    get_validation_transforms,
    get_inference_transforms
)


def test_transforms_output_shape_and_type():
    img = Image.new("RGB", (300, 400), color=(120, 180, 70))
    
    train_tf = get_training_transforms(image_size=(224, 224))
    val_tf = get_validation_transforms(image_size=(224, 224))
    infer_tf = get_inference_transforms(image_size=(224, 224))
    
    train_tensor = train_tf(img)
    val_tensor = val_tf(img)
    infer_tensor = infer_tf(img)
    
    assert isinstance(train_tensor, torch.Tensor)
    assert train_tensor.shape == (3, 224, 224)
    assert val_tensor.shape == (3, 224, 224)
    assert infer_tensor.shape == (3, 224, 224)


def test_validation_inference_consistency():
    img = Image.new("RGB", (250, 250), color=(50, 100, 150))
    
    val_tf = get_validation_transforms(image_size=(224, 224))
    infer_tf = get_inference_transforms(image_size=(224, 224))
    
    val_tensor = val_tf(img)
    infer_tensor = infer_tf(img)
    
    # Deterministic transforms must produce identical tensors
    assert torch.allclose(val_tensor, infer_tensor)
