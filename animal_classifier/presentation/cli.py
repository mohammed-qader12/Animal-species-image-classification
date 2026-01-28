import argparse
import sys
from pathlib import Path

# Ensure project root is in path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from animal_classifier.data.loaders.image_dataset_loader import ImageDatasetLoader
from animal_classifier.infrastructure.trainers.model_trainer import PyTorchTrainer
from animal_classifier.infrastructure.persistence.model_storage import PyTorchModelRepository
from animal_classifier.infrastructure.predictors.predictor_service import PyTorchImageClassifier
from animal_classifier.application.use_cases.train_classifier import TrainClassifier
from animal_classifier.application.use_cases.classify_image import ClassifyImage

def main():
    parser = argparse.ArgumentParser(description="Animal Species Image Classification System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    train_parser.add_argument("--output", type=str, default="model.pth", help="Output model filename")

    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Classify an image")
    predict_parser.add_argument("image", type=str, help="Path to image file")
    predict_parser.add_argument("--model", type=str, default="model.pth", help="Path to trained model")

    args = parser.parse_args()

    if args.command == "train":
        # Dependency Injection
        dataset_repo = ImageDatasetLoader()
        model_repo = PyTorchModelRepository()
        trainer = PyTorchTrainer()
        
        use_case = TrainClassifier(dataset_repo, trainer, model_repo)
        use_case.execute(epochs=args.epochs, save_name=args.output)
        
    elif args.command == "predict":
        dataset_repo = ImageDatasetLoader()
        model_repo = PyTorchModelRepository()
        classifier_service = PyTorchImageClassifier(dataset_repo)
        
        use_case = ClassifyImage(model_repo, classifier_service)
        try:
            result = use_case.execute(args.image, model_name=args.model)
            print("-" * 30)
            print(f"Prediction Result")
            print("-" * 30)
            print(f"Species: {result.species.common_name}")
            print(f"Scientific Name: {result.species.name}")
            print(f"Confidence: {result.confidence:.2%}")
            print("-" * 30)
        except Exception as e:
            print(f"Error: {e}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
