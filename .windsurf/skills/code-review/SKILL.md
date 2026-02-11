---
name: python-venv
description: Creates and manages Python virtual environments using uv with customizable arguments
---

# Python Virtual Environment Skill

## Usage

This skill helps you create and manage Python virtual environments using `uv`. You can customize the virtual environment name and Python version.

### Arguments
- `venv_name` (optional): Name of the virtual environment (default: "venv")
- `python_version` (optional): Python version to use (default: latest stable)
- `packages` (optional): List of packages to install (handles typos and case-insensitive)

## Commands

### Create Virtual Environment
```bash
# Basic usage
uv venv

# With custom name
uv venv {venv_name}

# With specific Python version
uv venv --python {python_version}

# With custom name and Python version
uv venv {venv_name} --python {python_version}
```

### Activate Virtual Environment
```bash
# Windows
{venv_name}\Scripts\activate

# Unix/Linux/Mac
source {venv_name}/bin/activate
```

### Install Dependencies
```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Install specific packages
uv pip install package-name

# Install with version
uv pip install package-name==version
```

### Smart Package Installation (LLM-Enhanced)
This skill can intelligently install packages with typo detection and PyPI validation:

```bash
# Smart install with typo correction
@python-venv install {packages}

# Examples:
# @python-venv install matplotlb scipy
# @python-venv install numpi, pandas, requests
# @python-venv install flask django numpy
```

#### Features:
- **Typo Detection**: Automatically detects and suggests corrections for common typos
- **Case-Insensitive**: Handles "NumPy", "numpy", "Numpy" etc.
- **PyPI Validation**: Checks if packages exist on PyPI before installation
- **Smart Suggestions**: Suggests similar package names for invalid packages
- **Batch Processing**: Installs multiple packages at once

#### Example Interactions:
```
User: @python-venv install matplotlb, scipy
Skill: Detected typo: "matplotlb" → "matplotlib"
Installing: matplotlib, scipy
✓ matplotlib 3.7.1 installed
✓ scipy 1.11.1 installed

User: @python-venv install numpi
Skill: Did you mean "numpy"? (numpi not found on PyPI)
Installing: numpy
✓ numpy 1.24.3 installed
```

### Deactivate Virtual Environment
```bash
deactivate
```

## Workflow Examples

### Example 1: Basic Project Setup
```bash
# Create virtual environment
uv venv

# Activate (Windows)
venv\Scripts\activate

# Install common packages
uv pip install requests pandas numpy

# Create requirements file
uv pip freeze > requirements.txt
```

### Example 2: Custom Environment
```bash
# Create environment with specific name and Python version
uv venv my-project-env --python 3.11

# Activate (Windows)
my-project-env\Scripts\activate

# Install project dependencies
uv pip install -r requirements-dev.txt
```

### Example 3: Smart Package Installation
```bash
# Create environment
uv venv

# Activate (Windows)
venv\Scripts\activate

# Smart install with typo correction
@python-venv install matplotlb, scipy, numpi, pandas

# Skill will:
# - Correct "matplotlb" → "matplotlib"
# - Correct "numpi" → "numpy"
# - Install all packages successfully
```

### Example 4: Data Science Project
```bash
# Create environment
uv venv data-science-env

# Activate
data-science-env\Scripts\activate

# Install data science packages
uv pip install jupyter pandas matplotlib seaborn scikit-learn
```

## Best Practices

1. **Always use virtual environments** for Python projects
2. **Add `venv/` to `.gitignore`** to avoid committing virtual environments
3. **Use `requirements.txt`** to track dependencies
4. **Specify Python versions** for reproducible environments
5. **Use descriptive names** for virtual environments

## Troubleshooting

### Common Issues
- **Permission errors**: Run terminal as administrator
- **Python not found**: Ensure Python is installed and in PATH
- **uv not found**: Install uv with `pip install uv` or follow official installation guide

### Useful Commands
```bash
# Check uv version
uv --version

# List available Python versions
uv python list

# Check current environment
uv pip list

# Upgrade pip
uv pip install --upgrade pip
```

## Integration with IDE

### VS Code
1. Activate virtual environment
2. Install Python extension
3. Select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
4. Choose the virtual environment's Python executable

### PyCharm
1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Navigate to `{venv_name}\Scripts\python.exe`
