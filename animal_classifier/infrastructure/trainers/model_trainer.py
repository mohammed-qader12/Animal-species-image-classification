import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from typing import List, Tuple, Any, Dict
import copy
import time

from animal_classifier.domain.services.trainer import Trainer
from animal_classifier.domain.entities.image import LabeledImage
from animal_classifier.infrastructure.models.cnn_classifier import SpeciesClassifier
from animal_classifier.infrastructure.pytorch_dataset import AnimalDataset
from animal_classifier.config import settings

class PyTorchTrainer(Trainer):
    """
    PyTorch implementation of the Trainer interface.
    """

    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = torch.device(device)
        print(f"Using device: {self.device}")

        # Define transforms
        self.data_transforms = {
            'train': transforms.Compose([
                transforms.Resize(settings.IMAGE_SIZE), # Resize first
                # Data Augmentation could go here (RandomHorizontalFlip etc)
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]),
            'val': transforms.Compose([
                transforms.Resize(settings.IMAGE_SIZE),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]),
        }

    def train(self, training_data: List[LabeledImage], validation_data: List[LabeledImage], epochs: int) -> Tuple[Any, Dict]:
        
        # Create Datasets and DataLoaders
        image_datasets = {
            'train': AnimalDataset(training_data, transform=self.data_transforms['train']),
            'val': AnimalDataset(validation_data, transform=self.data_transforms['val'])
        }
        
        dataloaders = {
            'train': DataLoader(image_datasets['train'], batch_size=settings.BATCH_SIZE, shuffle=True, num_workers=0), # num_workers=0 for Windows compatibility
            'val': DataLoader(image_datasets['val'], batch_size=settings.BATCH_SIZE, shuffle=False, num_workers=0)
        }
        
        dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
        
        # Model Setup
        model = SpeciesClassifier()
        model = model.to(self.device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
        # scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1) # Optional

        since = time.time()

        best_model_wts = copy.deepcopy(model.state_dict())
        best_acc = 0.0
        
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

        for epoch in range(epochs):
            print(f'Epoch {epoch}/{epochs - 1}')
            print('-' * 10)

            # Each epoch has a training and validation phase
            for phase in ['train', 'val']:
                if phase == 'train':
                    model.train()
                else:
                    model.eval()

                running_loss = 0.0
                running_corrects = 0

                # Iterate over data.
                if dataset_sizes[phase] == 0:
                    print(f"Skipping {phase} phase due to empty dataset.")
                    # Record dummy history or just continue
                    history[f'{phase}_loss'].append(0.0)
                    history[f'{phase}_acc'].append(0.0)
                    continue

                for inputs, labels in dataloaders[phase]:
                    inputs = inputs.to(self.device)
                    labels = labels.to(self.device)

                    # Zero the parameter gradients
                    optimizer.zero_grad()

                    # Forward
                    with torch.set_grad_enabled(phase == 'train'):
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)

                        # Backward + optimize only if in training phase
                        if phase == 'train':
                            loss.backward()
                            optimizer.step()

                    # Statistics
                    running_loss += loss.item() * inputs.size(0)
                    running_corrects += torch.sum(preds == labels.data)
                
                # if phase == 'train':
                #     scheduler.step()

                epoch_loss = running_loss / dataset_sizes[phase]
                epoch_acc = running_corrects.double() / dataset_sizes[phase]
                
                history[f'{phase}_loss'].append(epoch_loss)
                history[f'{phase}_acc'].append(epoch_acc.item())

                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

                # Deep copy the model
                if phase == 'val' and epoch_acc > best_acc:
                    best_acc = epoch_acc
                    best_model_wts = copy.deepcopy(model.state_dict())

            print()

        time_elapsed = time.time() - since
        print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'Best val Acc: {best_acc:4f}')

        # Load best model weights
        model.load_state_dict(best_model_wts)
        return model, history
