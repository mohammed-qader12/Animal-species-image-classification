import uvicorn
import sys
from pathlib import Path

# Add project root to python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

if __name__ == "__main__":
    # Import the app after setting up sys.path
    # using string import to avoid top-level import issues if run differently
    uvicorn.run("animal_classifier.presentation.api:app", host="0.0.0.0", port=8000, reload=True)
