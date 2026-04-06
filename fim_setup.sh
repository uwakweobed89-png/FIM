#!/bin/bash
# File Integrity Monitor - Setup Script

echo "======================================================"
echo "  File Integrity Monitor - Setup Wizard"
echo "======================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python $required_version+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r fim_requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp fim_env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your credentials:"
    echo "   nano .env"
    echo ""
else
    echo "ℹ️  .env file already exists"
fi

# Check config
if [ ! -f fim_config.yaml ]; then
    echo "❌ fim_config.yaml not found!"
    exit 1
else
    echo "✅ fim_config.yaml found"
fi

echo ""
echo "======================================================"
echo "  Setup Complete! 🎉"
echo "======================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Run in practice mode (safe testing):"
echo "   python file_integrity_monitor.py"
echo ""
echo "2. Watch how file changes are detected!"
echo ""
echo "3. Read the README for full documentation:"
echo "   cat FIM_README.md"
echo ""
echo "4. Switch to active mode when ready:"
echo "   Edit fim_config.yaml → mode: active"
echo ""
echo "Happy monitoring! 🔐"
