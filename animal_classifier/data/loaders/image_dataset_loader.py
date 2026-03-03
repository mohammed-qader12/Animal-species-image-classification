import json, random
from itertools import chain
from pathlib import Path
from typing import List, Tuple, Dict

from animal_classifier.domain.entities.species import Species
from animal_classifier.domain.entities.image import LabeledImage
from animal_classifier.domain.repositories.dataset_repository import DatasetRepository
from animal_classifier.config import settings

_BASE = Path(__file__).resolve().parent.parent.parent.parent
_LITE = _BASE / "dataset_lite"


def _resolve_paths() -> tuple:
    """Return (data_dir, translation_file) — prefers dataset_lite on Render."""
    if _LITE.exists():
        return _LITE, _LITE / "translation.json"
    return settings.DATASET_DIR, settings.TRANSLATION_FILE


class ImageDatasetLoader(DatasetRepository):
    """Loads labeled images from disk; auto-detects dataset_lite vs full archive."""

    def __init__(self, data_dir: Path = None, translation_file: Path = None):
        default_dir, default_trans = _resolve_paths()
        self.data_dir = data_dir or default_dir
        self.translation_file = translation_file or default_trans
        self._species: List[Species] = []
        self._images: Dict[str, List[LabeledImage]] = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        try:
            translations = json.loads(self.translation_file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            translations = {}

        for idx, d in enumerate(sorted(d for d in self.data_dir.iterdir() if d.is_dir())):
            sp = Species(id=idx, name=d.name, common_name=translations.get(d.name, d.name))
            imgs = [
                LabeledImage(path=str(p), species=sp)
                for p in chain.from_iterable(
                    d.glob(ext) for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp")
                )
            ]
            self._species.append(sp)
            self._images[sp.name] = imgs[:10] if settings.FAST_RUN else imgs

        self._loaded = True

    def get_all_species(self) -> List[Species]:
        self._load()
        return self._species

    def get_dataset_splits(self, train_ratio=0.7, val_ratio=0.15) -> Tuple[List, List, List]:
        self._load()
        if train_ratio + val_ratio >= 1.0:
            raise ValueError("Ratios must sum to less than 1.0")
        train, val, test = [], [], []
        for sp in self._species:
            imgs = list(self._images[sp.name])
            random.Random(settings.RANDOM_SEED + sp.id).shuffle(imgs)
            n_tr, n_val = int(len(imgs) * train_ratio), int(len(imgs) * val_ratio)
            train.extend(imgs[:n_tr])
            val.extend(imgs[n_tr : n_tr + n_val])
            test.extend(imgs[n_tr + n_val :])
        return train, val, test
