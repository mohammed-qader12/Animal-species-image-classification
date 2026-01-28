import os
import shutil
import random
from pathlib import Path

# Config
SOURCE_DIR = Path("archive/archive/dataset/dataset")
TARGET_DIR = Path("dataset_lite")
IMAGES_PER_CLASS = 5

def create_mini_dataset():
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return

    if TARGET_DIR.exists():
        print(f"Removing existing {TARGET_DIR}...")
        shutil.rmtree(TARGET_DIR)
    
    TARGET_DIR.mkdir(parents=True)
    print(f"Created {TARGET_DIR}")

    classes = [d for d in SOURCE_DIR.iterdir() if d.is_dir()]
    print(f"Found {len(classes)} classes.")

    total_images = 0
    for cls in classes:
        target_class_dir = TARGET_DIR / cls.name
        target_class_dir.mkdir()
        
        images = list(cls.glob("*.jpg"))
        # Take up to 5 random images
        selected = random.sample(images, min(len(images), IMAGES_PER_CLASS))
        
        for img in selected:
            shutil.copy2(img, target_class_dir / img.name)
            total_images += 1
            
    print(f"Done! Created lightweight dataset at '{TARGET_DIR}' with {total_images} images.")
    print("You can now upload 'dataset_lite' to GitHub instead of 'archive'.")

if __name__ == "__main__":
    create_mini_dataset()
