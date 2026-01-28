from abc import ABC, abstractmethod
from typing import Any
from animal_classifier.domain.entities.image import LabeledImage
from animal_classifier.application.dto.classification_result import ClassificationResult

class ImageClassifierService(ABC):
    """
    Abstract interface for running inference on an image.
    """
    
    @abstractmethod
    def predict(self, image_path: str, model: Any) -> ClassificationResult:
        """
        Predicts the species of the given image using the provided model.
        """
        pass
