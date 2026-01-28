import torch
from torchvision import transforms
from PIL import Image

from animal_classifier.domain.services.classifier import ImageClassifierService
from animal_classifier.application.dto.classification_result import ClassificationResult
from animal_classifier.domain.entities.species import Species
from animal_classifier.domain.repositories.dataset_repository import DatasetRepository
from animal_classifier.config import settings

class PyTorchImageClassifier(ImageClassifierService):
    
    def __init__(self, dataset_repo: DatasetRepository):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dataset_repo = dataset_repo
        
        # Cache species list for ID mapping
        # Note: This relies on the loading order being deterministic (which we ensured in ImageDatasetLoader)
        self.species_list = self.dataset_repo.get_all_species()

        self.transform = transforms.Compose([
            transforms.Resize(settings.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_path: str, model: Any) -> ClassificationResult:
        model = model.to(self.device)
        model.eval()
        
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Could not open image at {image_path}: {e}")
            
        input_tensor = self.transform(image).unsqueeze(0) # Add batch dimension
        input_tensor = input_tensor.to(self.device)
        
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            
        idx = predicted_idx.item()
        conf = confidence.item()
        
        if 0 <= idx < len(self.species_list):
            species = self.species_list[idx]
        else:
            # Fallback (should not happen if classes match)
            species = Species(id=idx, name="Unknown", common_name="Unknown")
            
        return ClassificationResult(species=species, confidence=conf)
