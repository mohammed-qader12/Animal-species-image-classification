from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Dict
from animal_classifier.domain.entities.image import LabeledImage

class Trainer(ABC):
    """
    Abstract interface for the model training service.
    """
    
    @abstractmethod
    def train(self, training_data: List[LabeledImage], validation_data: List[LabeledImage], epochs: int) -> Tuple[Any, Dict]:
        """
        Trains the model.
        Returns:
            - The trained model artifact (Any)
            - Training history/metrics (Dict)
        """
        pass
