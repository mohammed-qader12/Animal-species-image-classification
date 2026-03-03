import json
import random
from typing import List, Tuple, Dict
from pathlib import Path

from animal_classifier.domain.entities.species import Species
from animal_classifier.domain.entities.image import LabeledImage
from animal_classifier.domain.repositories.dataset_repository import DatasetRepository
from animal_classifier.config import settings

# Auto-detect dataset directory: prefer dataset_lite (for Render/GitHub),
# fall back to the full archive dataset if dataset_lite doesn't exist.
_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
_LITE_DIR = _BASE_DIR / "dataset_lite"
_LITE_TRANSLATION = _LITE_DIR / "translation.json"

def _resolve_dataset_dir() -> Path:
    if _LITE_DIR.exists():
        print(f"[DatasetLoader] Using dataset_lite: {_LITE_DIR}")
        return _LITE_DIR
    print(f"[DatasetLoader] Using full archive dataset: {settings.DATASET_DIR}")
    return settings.DATASET_DIR

def _resolve_translation_file() -> Path:
    if _LITE_TRANSLATION.exists():
        return _LITE_TRANSLATION
    return settings.TRANSLATION_FILE

class ImageDatasetLoader(DatasetRepository):
    """
    Concrete implementation of DatasetRepository.
    Loads images from the filesystem and handles stratified splitting.
    Automatically uses dataset_lite/ when the full archive dataset is unavailable
    (e.g. on Render or GitHub where archive/ is excluded from .gitignore).
    """

    def __init__(self, data_dir: Path = None, translation_file: Path = None):
        self.data_dir = data_dir if data_dir is not None else _resolve_dataset_dir()
        self.translation_file = translation_file if translation_file is not None else _resolve_translation_file()
        self._species_cache: List[Species] = []
        self._images_cache: Dict[str, List[LabeledImage]] = {} # Map species_name -> list of images
        self._loaded = False

    def _load_data(self):
        """
        Internal method to scan the directory and load metadata.
        """
        if self._loaded:
            return

        # Load translation map
        try:
            with open(self.translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Translation file not found at {self.translation_file}. Using directory names.")
            translations = {}

        # Scan directories
        species_list = []
        images_map = {}
        
        # Enumerate directories to assign IDs consistently
        # Sorting ensures deterministic ID assignment across runs
        dirs = sorted([d for d in self.data_dir.iterdir() if d.is_dir()])
        
        for idx, species_dir in enumerate(dirs):
            species_name = species_dir.name
            common_name = translations.get(species_name, species_name)
            
            species = Species(
                id=idx,
                name=species_name,
                common_name=common_name
            )
            species_list.append(species)
            
            # Scan images
            # Allowing common image extensions
            extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            species_images = []
            for ext in extensions:
                for img_path in species_dir.glob(ext):
                    labeled_image = LabeledImage(
                        path=str(img_path),
                        species=species
                    )
                    species_images.append(labeled_image)
            
            if settings.FAST_RUN and len(species_images) > 0:
                 # In fast run, take a small subset but ensure it's enough for train/val split if possible
                 # Or just take top 10
                 species_images = species_images[:10]

            images_map[species.name] = species_images

        self._species_cache = species_list
        self._images_cache = images_map
        self._loaded = True

    def get_all_species(self) -> List[Species]:
        self._load_data()
        return self._species_cache

    def get_dataset_splits(
        self, 
        train_ratio: float = 0.7, 
        val_ratio: float = 0.15
    ) -> Tuple[List[LabeledImage], List[LabeledImage], List[LabeledImage]]:
        
        self._load_data()
        
        # Check if ratios are valid
        if train_ratio + val_ratio >= 1.0:
            raise ValueError("Train and validation ratios must sum to less than 1.0")

        train_set = []
        val_set = []
        test_set = []

        # Stratified split
        for species in self._species_cache:
            images = self._images_cache[species.name]
            
            # Shuffle images for random split (using fixed seed from settings if needed, 
            # but usually handled by calling random.seed() before calling this)
            # Here we follow clean code, so we use the random module directly.
            # Assuming randomness is controlled externally or we can set it here.
            random.seed(settings.RANDOM_SEED) 
            # Note: Re-seeding inside the loop for every species with the SAME seed 
            # would cause identical shuffle patterns if list lengths are same. 
            # We should seed once outside or just rely on global state if set in main.
            # For safety, let's just use local Random instance to not mess with global state if we want strictness.
            # But specific requirements said "Application Layer use cases" manage logic. 
            # Loader just loads. Stratification is part of loading strategy here.
            
            # Better approach: shuffle once per list
            shuffled_images = list(images)
            random.Random(settings.RANDOM_SEED + species.id).shuffle(shuffled_images) # Salt seed with species ID for variance

            n_total = len(shuffled_images)
            n_train = int(n_total * train_ratio)
            n_val = int(n_total * val_ratio)
            # n_test is the rest

            train_set.extend(shuffled_images[:n_train])
            val_set.extend(shuffled_images[n_train:n_train + n_val])
            test_set.extend(shuffled_images[n_train + n_val:])

        return train_set, val_set, test_set
