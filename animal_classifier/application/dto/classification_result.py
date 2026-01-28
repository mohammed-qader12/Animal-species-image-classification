from dataclasses import dataclass
from animal_classifier.domain.entities.species import Species

@dataclass
class ClassificationResult:
    """
    Data Transfer Object for returning classification results.
    """
    species: Species
    confidence: float
