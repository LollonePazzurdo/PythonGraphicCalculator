# GraphicCalculator

A high-performance Python application with a CustomTkinter GUI for rendering 2D mathematical equations in real time. It uses vectorized NumPy meshgrids and parallel multi-threading for high performance.

## Installation & Setup

### 1. Clone the repository
```bash
git clone -b slow-simple https://github.com/LollonePazzurdo/PythonGraphicCalculator.git
cd PythonGraphicCalculator
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Using standard Python
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or if using `uv`: `uv pip install -r requirements.txt`)*

---

## Running the Application

### Launch GUI Calculator
```bash
python interface.pyw
```

### Run Benchmarks
```bash
python test_main.py
```
