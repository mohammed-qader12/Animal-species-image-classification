from animal_classifier.domain.repositories.model_repository import ModelRepository
from animal_classifier.domain.services.classifier import ImageClassifierService
from animal_classifier.application.dto.classification_result import ClassificationResult

class ClassifyImage:
    """
    Use Case: Classify a single image.
    """

    def __init__(
        self,
        model_repo: ModelRepository,
        classifier_service: ImageClassifierService
    ):
        self.model_repo = model_repo
        self.classifier_service = classifier_service

    def execute(self, image_path: str, model_name: str = "model.pth") -> ClassificationResult:
        model = self.model_repo.load(model_name)
        result = self.classifier_service.predict(image_path, model)
        return result
