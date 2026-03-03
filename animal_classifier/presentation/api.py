import random
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from animal_classifier.infrastructure.predictors.predictor_service import PyTorchImageClassifier
from animal_classifier.infrastructure.persistence.model_storage import PyTorchModelRepository
from animal_classifier.application.use_cases.classify_image import ClassifyImage
from animal_classifier.data.loaders.image_dataset_loader import ImageDatasetLoader

# ── Dependency Injection ──────────────────────────────────────────────────────
_dataset_repo = ImageDatasetLoader()
_use_case = ClassifyImage(PyTorchModelRepository(), PyTorchImageClassifier(_dataset_repo))
DATASET_PATH = _dataset_repo.data_dir  # reuses auto-resolved path (dataset_lite or archive)

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Animal Species Classifier API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.mount("/dataset", StaticFiles(directory=str(DATASET_PATH)), name="dataset")


# ── Schemas ───────────────────────────────────────────────────────────────────
class Prediction(BaseModel):
    species: str
    scientific_name: str
    confidence: float


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Animal Species Classifier API is running"}


@app.post("/predict", response_model=Prediction)
async def predict(file: UploadFile = File(...)):
    tmp = Path(f"temp_{file.filename}")
    try:
        tmp.write_bytes(await file.read())
        result = _use_case.execute(str(tmp), model_name="model.pth")
        return Prediction(
            species=result.species.common_name,
            scientific_name=result.species.name,
            confidence=result.confidence,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp.unlink(missing_ok=True)


@app.get("/examples")
def examples(species: str = None, limit: int = 6):
    if species:
        folder = DATASET_PATH / species
        if not folder.is_dir():
            return []
        imgs = list(folder.glob("*.jpg"))
        return [
            {"species": species, "url": f"/dataset/{img.relative_to(DATASET_PATH).as_posix()}"}
            for img in random.sample(imgs, min(limit, len(imgs)))
        ]

    folders = [d for d in DATASET_PATH.iterdir() if d.is_dir()]
    result = []
    for d in random.sample(folders, min(limit, len(folders))):
        imgs = list(d.glob("*.jpg"))
        if imgs:
            img = random.choice(imgs)
            result.append({"species": d.name, "url": f"/dataset/{img.relative_to(DATASET_PATH).as_posix()}"})
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
