import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from typing import List, Tuple, Any, Dict

from animal_classifier.domain.services.trainer import Trainer
from animal_classifier.domain.entities.image import LabeledImage
from animal_classifier.infrastructure.models.cnn_classifier import SpeciesClassifier
from animal_classifier.infrastructure.pytorch_dataset import AnimalDataset
from animal_classifier.config import settings

_NORM = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])


class PyTorchTrainer(Trainer):
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = torch.device(device)
        self.transform = transforms.Compose([
            transforms.Resize(settings.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(*_NORM),
        ])

    def _loader(self, data: List[LabeledImage], shuffle: bool) -> DataLoader:
        return DataLoader(
            AnimalDataset(data, self.transform),
            batch_size=settings.BATCH_SIZE, shuffle=shuffle, num_workers=0,
        )

    def _run_phase(self, model, loader, criterion, optimizer, train: bool) -> Tuple[float, float]:
        if len(loader.dataset) == 0:
            return 0.0, 0.0
        model.train() if train else model.eval()
        total_loss = total_correct = 0
        for inputs, labels in loader:
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            optimizer.zero_grad()
            with torch.set_grad_enabled(train):
                out = model(inputs)
                loss = criterion(out, labels)
                if train:
                    loss.backward()
                    optimizer.step()
            total_loss += loss.item() * inputs.size(0)
            total_correct += (out.argmax(1) == labels).sum().item()
        n = len(loader.dataset)
        return total_loss / n, total_correct / n

    def train(self, training_data: List[LabeledImage], validation_data: List[LabeledImage], epochs: int) -> Tuple[Any, Dict]:
        model = SpeciesClassifier().to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
        loaders = {"train": self._loader(training_data, True), "val": self._loader(validation_data, False)}
        history = {k: [] for k in ("train_loss", "train_acc", "val_loss", "val_acc")}
        best_wts, best_acc = copy.deepcopy(model.state_dict()), 0.0

        for ep in range(epochs):
            for phase, is_train in (("train", True), ("val", False)):
                loss, acc = self._run_phase(model, loaders[phase], criterion, optimizer, is_train)
                history[f"{phase}_loss"].append(loss)
                history[f"{phase}_acc"].append(acc)
                print(f"Epoch {ep} | {phase}: loss={loss:.4f}  acc={acc:.4f}")
                if not is_train and acc > best_acc:
                    best_acc, best_wts = acc, copy.deepcopy(model.state_dict())

        model.load_state_dict(best_wts)
        print(f"Best val acc: {best_acc:.4f}")
        return model, history
