import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_ROOT = BASE_DIR / "archive" / "archive"
DATASET_DIR = DATA_ROOT / "dataset" / "dataset"
TRANSLATION_FILE = DATA_ROOT / "translation.json"

# Random seed for reproducibility
RANDOM_SEED = 42

# Image constants
IMAGE_SIZE = (224, 224) 
BATCH_SIZE = 32
NUM_CLASSES = 153 

# Debug flags
FAST_RUN = False # Use a subset of data for quick verification
