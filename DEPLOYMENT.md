# Deployment Guide

This guide explains how to deploy the **Animal Species Classifier Backend** to a server.

## Method 1: Docker (Recommended)

Docker packages the application and all its dependencies into a single container, making it easy to run on any server (AWS, DigitalOcean, Azure, locally).

### 1. Build the Docker Image
Run this command in the project root (where `Dockerfile` is):

```bash
docker build -t animal-classifier-api .
```
*(This may take a few minutes as it downloads PyTorch)*

### 2. Run the Container
```bash
docker run -d -p 8000:8000 --name api animal-classifier-api
```
The API will now be accessible at `http://your-server-ip:8000`.

### 3. Check Logs
```bash
docker logs -f api
```

---

## Method 2: Manual Deployment (VPS)

If you have a Linux server (Ubuntu/Debian):

1.  **Clone the code** to the server.
2.  **Install Python 3.8+**.
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run with Systemd (Keep it alive)**:
    Create a file `/etc/systemd/system/animal-api.service`:
    ```ini
    [Unit]
    Description=Animal Classifier API
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/path/to/project
    ExecStart=/usr/bin/python3 run_api.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
5.  **Start the Service**:
    ```bash
    sudo systemctl enable animal-api
    sudo systemctl start animal-api
    ```

## Important Notes

1.  **Dataset**: The Docker image copies the dataset into the container. If your dataset is huge, you should stick to Method 2 or use Docker Volumes.
2.  **Model**: Ensure `model.pth` is generated (train the model) before building the Docker image, OR train it inside the container.
