from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import random
from pathlib import Path
import json

# Import our domain/application logic
from animal_classifier.infrastructure.predictors.predictor_service import PyTorchImageClassifier
from animal_classifier.infrastructure.persistence.model_storage import PyTorchModelRepository
from animal_classifier.application.use_cases.classify_image import ClassifyImage
from animal_classifier.data.loaders.image_dataset_loader import ImageDatasetLoader
from animal_classifier.config import settings

app = FastAPI(title="Animal Species Classifier API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves static files from the dataset directory
# This allows the frontend to display example images directly from disk
# Check for dataset_lite first (Mini dataset for GitHub deployment)
LITE_DATASET_DIR = Path("dataset_lite")
if LITE_DATASET_DIR.exists():
    DATASET_PATH = LITE_DATASET_DIR
    print("Using lite dataset for examples.")
else:
    DATASET_PATH = settings.DATASET_DIR
    print("Using full archive dataset for examples.")

app.mount("/dataset", StaticFiles(directory=str(DATASET_PATH)), name="dataset")

# Dependency Injection Setup
# We load the model once at startup to avoid reloading per request
model_repo = PyTorchModelRepository()
dataset_repo = ImageDatasetLoader() # Only needed if we want species info or scan dirs
classifier_service = PyTorchImageClassifier(dataset_repo)
classify_use_case = ClassifyImage(model_repo, classifier_service)

# Load model (assuming 'model.pth' exists from training)
MODEL_PATH = "model.pth"
if not os.path.exists(MODEL_PATH):
    print(f"Warning: {MODEL_PATH} not found. Predictions will fail.")

@app.get("/")
def read_root():
    return {"message": "Animal Species Classifier API is running"}

class PredictionResponse(BaseModel):
    species: str
    scientific_name: str
    confidence: float

@app.post("/predict", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_file = Path(f"temp_{file.filename}")
    try:
        with temp_file.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run prediction
        # We catch exceptions to handle cases where model isn't loaded or image is bad
        try:
            result = classify_use_case.execute(str(temp_file), model_name=MODEL_PATH)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        return PredictionResponse(
            species=result.species.common_name,
            scientific_name=result.species.name,
            confidence=result.confidence
        )
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()

@app.get("/examples")
def get_examples(species: str = None, limit: int = 6):
    """
    Returns a list of image URLs from the dataset.
    If species is provided, returns images of that species.
    Otherwise, returns random images.
    """
    if not DATASET_PATH.exists():
        return []

    result = []
    
    if species:
        # User requested specific species (scientific name expected)
        # Search for exact folder match first
        target_folder = DATASET_PATH / species
        
        if not target_folder.exists() or not target_folder.is_dir():
            # Try finding folder that looks like the species name (partial match or fuzzy)
            # But scientific name should be exact from our prediction
            return []
            
        images = list(target_folder.glob("*.jpg"))
        # Get random sample of this species
        selected_images = random.sample(images, min(len(images), limit))
        
        for img in selected_images:
            rel_path = img.relative_to(DATASET_PATH)
            url = f"/dataset/{rel_path.as_posix()}"
            result.append({
                "species": species,
                "url": url
            })
            
    else:
        # Random logic (existing)
        species_folders = [d for d in DATASET_PATH.iterdir() if d.is_dir()]
        selected_folders = random.sample(species_folders, min(len(species_folders), limit))
        
        for folder in selected_folders:
            images = list(folder.glob("*.jpg"))
            if images:
                img = random.choice(images)
                rel_path = img.relative_to(DATASET_PATH)
                url = f"/dataset/{rel_path.as_posix()}" 
                result.append({
                    "species": folder.name, 
                    "url": url
                })
            
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
