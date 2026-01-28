from animal_classifier.domain.repositories.dataset_repository import DatasetRepository
from animal_classifier.domain.repositories.model_repository import ModelRepository
from animal_classifier.domain.services.trainer import Trainer

class TrainClassifier:
    """
    Use Case: Train the animal species classifier.
    """

    def __init__(
        self, 
        dataset_repo: DatasetRepository, 
        trainer: Trainer, 
        model_repo: ModelRepository
    ):
        self.dataset_repo = dataset_repo
        self.trainer = trainer
        self.model_repo = model_repo

    def execute(self, epochs: int = 10, save_name: str = "model.pth") -> dict:
        print("Loading dataset...")
        train_data, val_data, _ = self.dataset_repo.get_dataset_splits()
        print(f"Training on {len(train_data)} images, Validating on {len(val_data)} images.")

        print("Starting training...")
        model, history = self.trainer.train(train_data, val_data, epochs)

        print(f"Saving model to {save_name}...")
        self.model_repo.save(model, save_name)
        
        return history
