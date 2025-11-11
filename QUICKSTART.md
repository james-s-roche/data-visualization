# Quick Start Guide

## 🐳 Docker (Fastest & Easiest)

### Build and Start Everything
```bash
cd /Users/james/code/portfolio/data_exploration
docker-compose up --build
```

**What this does:**
- Builds Docker image from `Dockerfile`
- Starts EDA Dashboard on `http://localhost:8050`
- Starts Dash Plotter on `http://localhost:8051`
- Mounts your project directory for live code changes

**Access the apps:**
- **EDA Dashboard:** http://localhost:8050
- **Dash Plotter:** http://localhost:8051

### Other Docker Commands

**Run in background:**
```bash
docker-compose up -d --build
```

**Stop services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild image (if you changed requirements.txt):**
```bash
docker-compose build --no-cache
```

**Only build image (don't start):**
```bash
docker build -t data-visualization .
```

**Run single service:**
```bash
docker run -p 8050:8050 -v $(pwd):/app data-visualization python eda_dashboard.py
```

---

## 🐍 Python (Local Environment)

### One-Time Setup
```bash
cd /Users/james/code/portfolio/data_exploration

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Apps
```bash
# EDA Dashboard
python eda_dashboard.py

# Dash Plotter
python dash_plotter.py
```

Then open: `http://127.0.0.1:8050`

---

## 📋 File Reference

| File | Purpose |
|------|---------|
| `eda_dashboard.py` | ⭐ Main app: 4 tabs for comprehensive data analysis |
| `dash_plotter.py` | Lightweight plotting app (single plot view) |
| `simple_plotter.py` | CLI script for one-off scatter plots |
| `Dockerfile` | Docker container definition |
| `docker-compose.yml` | Multi-service Docker setup (dashboard + plotter) |
| `requirements.txt` | Python package dependencies |
| `README.md` | Full documentation |
| `DOCKER_SETUP.md` | Detailed Docker guide |

---

## 🎯 Which Should I Use?

**Choose Docker if:**
- You don't have Python/virtual env set up
- You want consistent environment across machines
- You like one-command startup
- You're on macOS/Linux and want to avoid venv issues

**Choose Python if:**
- You're comfortable with virtual environments
- You want faster iteration (no rebuild needed)
- You're doing active development

**Recommended:** Start with Docker!

---

## 🚀 Next Steps

1. **Install Docker** (if not already): https://www.docker.com/products/docker-desktop

2. **Start apps:**
   ```bash
   docker-compose up --build
   ```

3. **Open in browser:**
   - EDA Dashboard: http://localhost:8050
   - Dash Plotter: http://localhost:8051

4. **Upload data** or use default `tips` dataset

5. **Explore!** Try all 4 tabs in the EDA Dashboard

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Docker daemon is not running" | Open Docker Desktop |
| "Port 8050 already in use" | Stop container or use different port |
| "ModuleNotFoundError" | Run `docker-compose build --no-cache` |
| "Can't access localhost:8050" | Try `http://127.0.0.1:8050` instead |
| "Changes not reflected in container" | Rebuild: `docker-compose build --no-cache` |

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for more details.

---

**Happy exploring! 📊**
