# Animal Species Image Classification

This repository contains two main components:

1. **Web App**: A frontend application for interacting with the animal classification system.
2. **Animal Classifier**: A backend system for classifying animal species using machine learning models.

## Clone the Repository

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/mohammed-qader12/Animal-species-image-classification.git
cd Animal-species-image-classification
```

## Web App Setup

The `web_app` directory contains the frontend application. Follow these steps to set it up:

1. Navigate to the `web_app` directory:
   ```bash
   cd web_app
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The web app will be available at `http://localhost:3000`.

## Animal Classifier Setup

The `animal_classifier` directory contains the backend system. Follow these steps to set it up:

1. Navigate to the `animal_classifier` directory:
   ```bash
   cd animal_classifier
   ```

2. Set up a Python virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend system:
   ```bash
   python main.py
   ```

The backend system will start and be ready to process requests.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.