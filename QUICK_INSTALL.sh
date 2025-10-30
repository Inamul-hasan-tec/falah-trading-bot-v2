#!/bin/bash
# Quick installation script - installs packages one by one

echo "🚀 Installing core packages..."

# Install one by one so you can see progress
pip install --no-cache-dir numpy
pip install --no-cache-dir pandas
pip install --no-cache-dir pyyaml
pip install --no-cache-dir python-dotenv
pip install --no-cache-dir kiteconnect

echo "✅ Core packages installed!"
echo ""
echo "Testing imports..."
python -c "import pandas; import numpy; import yaml; from kiteconnect import KiteConnect; print('✅ All core packages working!')"
