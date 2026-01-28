from dataclasses import dataclass
from animal_classifier.domain.entities.species import Species

@dataclass(frozen=True)
class LabeledImage:
    """
    Represents a single image sample with its ground truth label.
    """
    path: str
    species: Species
