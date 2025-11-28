# Maveric Developer Guide

A comprehensive guide for setting up and working with the Maveric RIC Algorithm Development Platform (RADP).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Core RADP Setup](#core-radp-setup)
5. [Services Setup](#services-setup)
6. [Applications Setup](#applications-setup)
7. [Notebooks Setup](#notebooks-setup)
8. [Testing Setup](#testing-setup)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

For developers who want to get up and running quickly:

```bash
# 1. Clone and navigate to the repository
git clone <repository-url>
cd maveric

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip3 install --upgrade pip

# 3. Set environment variables
export PYTHONPATH="$(pwd)":$PYTHONPATH
cp .env-dev .env

# 4. Install core dependencies
pip3 install -r requirements-dev.txt
pip3 install -r radp/client/requirements.txt
pip3 install -r radp/common/requirements.txt
pip3 install -r radp/digital_twin/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
pip3 install -r radp/utility/requirements.txt

# 5. Start RADP services
docker build -t radp radp
docker compose -f dc.yml -f dc-dev.yml up -d --build

# 6. Verify setup
python3 apps/example/example_app.py
```

---

## Prerequisites

### System Requirements
- **Python**: 3.8.x to 3.10.x (3.11.x not yet supported due to PyTorch compatibility)
- **Docker**: Latest version with Docker Compose support
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended for training)
- **Storage**: At least 10GB free space

### Optional Requirements
- **CUDA**: For GPU acceleration (requires NVIDIA drivers and CUDA toolkit)
- **ffmpeg**: For video generation in notebooks

---

## Environment Setup

### 1. Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Upgrade pip
pip3 install --upgrade pip
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from development template
cp .env-dev .env
```

Edit `.env` with your local paths:

```bash
# Required: Path to ffmpeg binary (for notebooks)
FFMPEG_PATH="/usr/local/bin/ffmpeg"  # macOS with Homebrew
# FFMPEG_PATH="/usr/bin/ffmpeg"      # Linux
# FFMPEG_PATH="C:\\ffmpeg\\bin\\ffmpeg.exe"  # Windows

# RADP Service Configuration
RADP_SERVICE_IP=127.0.0.1
RADP_SERVICE_PORT=8081  # Development port
# RADP_SERVICE_PORT=8080  # Production port
```

### 3. Python Path Configuration

**Critical**: Set the PYTHONPATH to include the project root:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PYTHONPATH="$(pwd)":$PYTHONPATH

# Or run before each development session
export PYTHONPATH="/path/to/maveric":$PYTHONPATH
```

---

## Core RADP Setup

The RADP (RIC Algorithm Development Platform) is the core library providing RF simulation and digital twin capabilities.

### Installation Order

Install RADP dependencies in this specific order:

```bash
# 1. Core development dependencies
pip3 install -r requirements-dev.txt

# 2. RADP client (API communication)
pip3 install -r radp/client/requirements.txt

# 3. RADP common utilities
pip3 install -r radp/common/requirements.txt

# 4. RADP digital twin (with PyTorch CPU support)
pip3 install -r radp/digital_twin/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 5. RADP utility functions
pip3 install -r radp/utility/requirements.txt
```

### Dependencies Overview

| Component | Purpose | Key Dependencies |
|-----------|---------|------------------|
| `radp/client` | API client for RADP services | pandas, requests, pyarrow |
| `radp/common` | Shared utilities and constants | - |
| `radp/digital_twin` | RF simulation and ML models | torch, gpytorch, scikit-learn |
| `radp/utility` | Helper utilities | pandas, numpy |

### Docker Setup for RADP

```bash
# Build RADP Docker image
docker build -t radp radp

# For GPU support (if you have NVIDIA GPU)
docker build -f radp/Dockerfile-cuda -t radp radp
```

---

## Services Setup

The services layer provides backend functionality for training, orchestration, and data processing.

### Service Dependencies

Install all service requirements:

```bash
# Development tools for services
pip3 install -r services/requirements-dev.txt

# Individual service dependencies
pip3 install -r services/api_manager/requirements.txt
pip3 install -r services/orchestration/requirements.txt
pip3 install -r services/rf_prediction/requirements.txt
pip3 install -r services/training/requirements.txt
pip3 install -r services/ue_tracks_generation/requirements.txt
```

### Service Architecture

| Service | Purpose | Port | Dependencies |
|---------|---------|------|--------------|
| `api_manager` | REST API gateway | 8080/8081 | FastAPI, Kafka |
| `orchestration` | Job orchestration | - | Kafka, Redis |
| `training` | ML model training | - | PyTorch, GPyTorch |
| `rf_prediction` | RF simulation | - | NumPy, SciPy |
| `ue_tracks_generation` | UE mobility simulation | - | NumPy, Pandas |

### Starting Services

```bash
# Development mode
docker compose -f dc.yml -f dc-dev.yml up -d --build

# Production mode
docker compose -f dc.yml -f dc-prod.yml up -d --build

# With GPU support
docker compose -f dc.yml -f dc-dev.yml -f dc-cuda.yml up -d --build
```

---

## Applications Setup

The applications layer contains example implementations and use cases.

### Applications Overview

| Application | Purpose | Key Features |
|-------------|---------|--------------|
| `example` | Basic RADP usage | Simple simulation example |
| `coverage_capacity_optimization` | CCO algorithms | RL-based optimization |
| `energy_savings` | Energy efficiency | Dynamic power management |
| `load_balancing` | Load distribution | Traffic-aware optimization |
| `mobility_robustness_optimization` | MRO algorithms | Handover optimization |

### Installation

```bash
# Install application dependencies
pip3 install -r apps/requirements.txt

# Additional dependencies for specific apps
# Energy Savings App (if using RL)
pip3 install gymnasium stable-baselines3[extra] torch

# Load Balancing App
pip3 install gymnasium stable-baselines3[extra] matplotlib

# MRO App
pip3 install scikit-learn matplotlib seaborn
```

### Running Examples

```bash
# Basic example
python3 apps/example/example_app.py

# Coverage and Capacity Optimization
python3 apps/coverage_capacity_optimization/cco_example_app.py

# Energy Savings (requires trained models)
python3 apps/energy_savings/main_app.py --infer --tick 0

# Load Balancing (requires trained models)
python3 apps/load_balancing/main_app.py --infer --tick 0
```

---

## Notebooks Setup

Jupyter notebooks provide interactive examples and data analysis capabilities.

### Installation

```bash
# Install notebook dependencies
pip3 install -r notebooks/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Optional: Enable Jupyter extensions
jupyter nbextension enable codefolding/main
```

### Key Notebooks

| Notebook | Purpose | Requirements |
|----------|---------|--------------|
| `coo_with_radp_digital_twin.ipynb` | Coverage optimization demo | Sample data |
| `energy_savings.ipynb` | Energy efficiency analysis | Trained models |
| `load_balancing.ipynb` | Load balancing examples | Trained models |
| `mobility_model.ipynb` | Mobility pattern analysis | Sample data |
| `mro.ipynb` | Mobility robustness optimization | Sample data |
| `traffic_demand_demonstration.ipynb` | Traffic simulation | Generated data |

### Sample Data Setup

```bash
# Extract sample data
cd notebooks/data
unzip sim_data.zip
unzip mro_data.zip
unzip energy_saving_data.zip
unzip load_balancing_data.zip
```

### Starting Jupyter

```bash
# Start Jupyter notebook server
jupyter notebook

# Or start JupyterLab
jupyter lab
```

---

## Testing Setup

### Test Dependencies

```bash
# Install test dependencies
pip3 install -r tests/requirements.txt

# For CUDA testing (if applicable)
pip3 install -r tests/cuda/requirements.txt
```

### Running Tests

```bash
# Unit tests
pytest

# Component tests
python3 tests/run_component_tests.py

# End-to-end tests
python3 tests/run_end_to_end_tests.py

# Validation tests
python3 tests/run_validation_tests.py
```

---

## Development Workflow

### 1. Development Branch Setup

```bash
# Pull latest main branch
git checkout main
git pull origin main

# Create development branch
git checkout -b feature/your-feature-name
```

### 2. Code Changes and Testing

```bash
# Make your changes
# ... edit files ...

# Run tests
pytest

# Run component tests
python3 tests/run_component_tests.py

# Run pre-commit checks
pre-commit install
python3 -m pre_commit run --all-files
```

### 3. Local Service Testing

```bash
# Start services in development mode
docker compose -f dc.yml -f dc-dev.yml up -d --build

# Test with example application
python3 apps/example/example_app.py

# Monitor services
docker logs -f radp_dev-api-manager-1
```

### 4. Commit and Push

```bash
# Commit with descriptive message
git add .
git commit -m "Add feature: brief description"

# Push to remote
git push origin feature/your-feature-name

# Create pull request
```

---

## Troubleshooting

### Common Issues

#### 1. PYTHONPATH Not Set
**Error**: `ModuleNotFoundError: No module named 'radp'`
**Solution**: 
```bash
export PYTHONPATH="$(pwd)":$PYTHONPATH
```

#### 2. Docker Permission Issues
**Error**: `Permission denied` when running Docker commands
**Solution**:
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# On macOS/Windows, ensure Docker Desktop is running
```

#### 3. Port Conflicts
**Error**: `Port already in use`
**Solution**:
```bash
# Check what's using the port
lsof -i :8081  # macOS/Linux
netstat -ano | findstr :8081  # Windows

# Stop conflicting services or change ports in .env
```

#### 4. CUDA/PyTorch Issues
**Error**: CUDA-related errors
**Solution**:
```bash
# Use CPU-only PyTorch
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or ensure CUDA compatibility
nvidia-smi  # Check CUDA installation
```

#### 5. Memory Issues
**Error**: Out of memory during training
**Solution**:
```bash
# Reduce batch size in training scripts
# Use smaller datasets for testing
# Ensure sufficient RAM (16GB+ recommended)
```

### Getting Help

1. **Check logs**: `docker logs <container-name>`
2. **Verify services**: `docker ps`
3. **Test connectivity**: `curl http://localhost:8081/health`
4. **Review documentation**: Check specific README files in each module

### Useful Commands

```bash
# Clean up Docker resources
docker system prune -a

# Reset virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Check service status
docker compose -f dc.yml -f dc-dev.yml ps

# View service logs
docker compose -f dc.yml -f dc-dev.yml logs -f
```

---

## Quick Reference

### Essential Commands

```bash
# Setup (run once)
python3 -m venv .venv && source .venv/bin/activate
pip3 install --upgrade pip
export PYTHONPATH="$(pwd)":$PYTHONPATH
cp .env-dev .env

# Install dependencies
pip3 install -r requirements-dev.txt
pip3 install -r radp/client/requirements.txt
pip3 install -r radp/common/requirements.txt
pip3 install -r radp/digital_twin/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
pip3 install -r radp/utility/requirements.txt
pip3 install -r services/requirements-dev.txt
pip3 install -r services/api_manager/requirements.txt
pip3 install -r services/orchestration/requirements.txt
pip3 install -r services/rf_prediction/requirements.txt
pip3 install -r services/training/requirements.txt
pip3 install -r services/ue_tracks_generation/requirements.txt
pip3 install -r apps/requirements.txt

# Start services
docker build -t radp radp
docker compose -f dc.yml -f dc-dev.yml up -d --build

# Test setup
python3 apps/example/example_app.py

# Run tests
pytest
```

### Directory Structure

```
maveric/
├── radp/                    # Core RADP library
├── services/                # Backend services
├── apps/                    # Example applications
├── notebooks/               # Jupyter notebooks
├── tests/                   # Test suites
├── requirements-dev.txt     # Development dependencies
├── .env-dev                 # Development environment
├── .env-prod                # Production environment
├── dc.yml                   # Docker Compose base
├── dc-dev.yml               # Docker Compose development
└── dc-prod.yml              # Docker Compose production
```

---

## License

See [LICENSE](LICENSE) file for details.
