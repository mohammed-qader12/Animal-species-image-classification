import sys
from pathlib import Path

# Add project root to python path to allow imports work correctly
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from animal_classifier.presentation.cli import main

if __name__ == "__main__":
    main()
