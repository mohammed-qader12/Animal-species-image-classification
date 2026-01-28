import torch
from typing import Any
from pathlib import Path

from animal_classifier.domain.repositories.model_repository import ModelRepository
from animal_classifier.infrastructure.models.cnn_classifier import SpeciesClassifier
from animal_classifier.config import settings

class PyTorchModelRepository(ModelRepository):
    """
    Saves and loads models using torch.save/load.
    Stores state_dict for best practice.
    """

    def save(self, model: Any, name: str):
        # We assume 'name' is just a filename, saving to current dir or a models dir?
        # Let's save to a specific 'models' directory if possible, or just local.
        # User requested "infrastructure/persistence/model_storage.py"
        # Let's just use the name provided as path.
        path = name
        torch.save(model.state_dict(), path)
        print(f"Model state dictionary saved to {path}")

    def load(self, name: str) -> Any:
        model = SpeciesClassifier()
        # Ensure we map to the correct device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(torch.load(name, map_location=device))
        model.to(device)
        model.eval() # Set to eval mode by default
        return model
