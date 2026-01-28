from torch.utils.data import Dataset
from PIL import Image
from typing import List
from animal_classifier.domain.entities.image import LabeledImage

class AnimalDataset(Dataset):
    """
    PyTorch Dataset wrapper for the domain LabeledImage entities.
    """
    def __init__(self, labeled_images: List[LabeledImage], transform=None):
        self.labeled_images = labeled_images
        self.transform = transform

    def __len__(self):
        return len(self.labeled_images)
    
    def __getitem__(self, idx):
        item = self.labeled_images[idx]
        try:
            image = Image.open(item.path).convert("RGB")
        except Exception as e:
            # Handle corrupt images or errors? 
            # For now, print error and return a black image or raise?
            # Better to be robust: return a dummy or skip (Datalaoder handles skpping hard).
            # Let's just raise so we know data is bad.
            print(f"Error loading image {item.path}: {e}")
            raise e
            
        label = item.species.id 
        
        if self.transform:
            image = self.transform(image)
            
        return image, label
