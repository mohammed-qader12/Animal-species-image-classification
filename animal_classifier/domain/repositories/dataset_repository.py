from abc import ABC, abstractmethod
from typing import List, Tuple
from animal_classifier.domain.entities.species import Species
from animal_classifier.domain.entities.image import LabeledImage

class DatasetRepository(ABC):
    """
    Abstract interface for accessing the dataset.
    Follows the Repository pattern to decouple domain from data sources.
    """

    @abstractmethod
    def get_all_species(self) -> List[Species]:
        """
        Retrieves all available species in the dataset.
        """
        pass

    @abstractmethod
    def get_dataset_splits(
        self, 
        train_ratio: float = 0.7, 
        val_ratio: float = 0.15
    ) -> Tuple[List[LabeledImage], List[LabeledImage], List[LabeledImage]]:
        """
        Partitions the dataset into training, validation, and test sets.
        
        Args:
            train_ratio: Proportion of data for training (default 0.7)
            val_ratio: Proportion of data for validation (default 0.15)
            
        Returns:
            Tuple containing (train_set, val_set, test_set).
            Each set is a list of LabeledImage objects.
        """
        pass
