# Docker Setup Guide

## Prerequisites
- Docker installed ([Download Docker Desktop](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

## Building the Docker Image

### Option 1: Build and Run with Docker Compose (Easiest)

Build and start both services:
```bash
cd /Users/james/code/portfolio/data_exploration
docker-compose up --build
```

This will:
- Build the Docker image from the Dockerfile
- Start the EDA Dashboard on `http://localhost:8050`
- Start the Dash Plotter on `http://localhost:8051`

To run in background:
```bash
docker-compose up -d --build
```

Stop the services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

---

### Option 2: Build and Run Individual Services

**Build the image:**
```bash
cd /Users/james/code/portfolio/data_exploration
docker build -t data-visualization .
```

**Run EDA Dashboard:**
```bash
docker run -p 8050:8050 -v $(pwd):/app data-visualization python eda_dashboard.py
```

**Run Dash Plotter:**
```bash
docker run -p 8051:8050 -v $(pwd):/app data-visualization python dash_plotter.py
```

---

## Common Commands

### View running containers
```bash
docker ps
```

### Stop a container
```bash
docker stop <container_id>
```

### Remove image
```bash
docker rmi data-visualization
```

### Rebuild image (if you updated requirements.txt)
```bash
docker-compose build --no-cache
```

### Access container shell (for debugging)
```bash
docker exec -it data-viz-eda /bin/bash
```

---

## Troubleshooting

**"Docker daemon is not running"**
- Open Docker Desktop from Applications

**"Port 8050 is already in use"**
- Stop the running container: `docker stop <container_id>`
- Or change the port mapping in `docker-compose.yml`

**"ModuleNotFoundError" inside container**
- Rebuild the image: `docker-compose build --no-cache`

**Can't access the app**
- Verify Docker is running: `docker ps`
- Check if container is running: `docker logs <container_id>`
- Try `http://127.0.0.1:8050` instead of `localhost:8050` (Windows/some configs)

---

## What's in the Docker Image?

- Python 3.11 slim base image
- All dependencies from `requirements.txt` (pandas, plotly, dash, scipy)
- Your project files mounted as a volume
- Port 8050 exposed for Dash apps

The image is lightweight (~500MB) and includes only essential dependencies.

---

## Next Steps

1. Install Docker Desktop
2. Run: `docker-compose up --build`
3. Open: `http://localhost:8050` (EDA Dashboard) or `http://localhost:8051` (Dash Plotter)
4. Test with a CSV file or default dataset
