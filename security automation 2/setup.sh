#!/bin/bash
# Quick Setup Script for Login Detector

echo "============================================"
echo "  Login Detector - Setup Wizard"
echo "============================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.10"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your credentials:"
    echo "   nano .env"
    echo ""
else
    echo "ℹ️  .env file already exists"
fi

# Check if config.yaml exists
if [ ! -f config.yaml ]; then
    echo "❌ config.yaml not found!"
    echo "   This file should have been created. Please check the files."
    exit 1
else
    echo "✅ config.yaml found"
fi

echo ""
echo "============================================"
echo "  Setup Complete! 🎉"
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure credentials:"
echo "   nano .env"
echo ""
echo "2. Run in practice mode (safe testing):"
echo "   python login_detector_modernized.py"
echo ""
echo "3. Or edit config.yaml to switch modes:"
echo "   mode: active  # For production monitoring"
echo ""
echo "4. Check README.md for full documentation"
echo ""
echo "Happy monitoring! 🔐"
