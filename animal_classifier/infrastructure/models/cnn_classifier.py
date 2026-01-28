import torch
import torch.nn as nn
from torchvision import models
from animal_classifier.config import settings

class SpeciesClassifier(nn.Module):
    """
    CNN model for animal species classification.
    Uses a pretrained ResNet18 backbone.
    """
    def __init__(self, num_classes: int = settings.NUM_CLASSES):
        super().__init__()
        # Use ResNet18 with default (ImageNet) weights
        # We assume the user has internet access for the first run to download weights.
        # If not, we might need a local weight file, but standard practice allows downloading.
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        
        # Replace the final fully connected layer
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_ftrs, num_classes)
        
    def forward(self, x):
        return self.backbone(x)
