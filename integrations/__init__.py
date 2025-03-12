"""
Integrations package for Personal Assistant

This package provides integrations with various services.
"""

from pathlib import Path

# Create necessary directories
CREDENTIALS_DIR = Path("credentials")
CREDENTIALS_DIR.mkdir(exist_ok=True)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True) 