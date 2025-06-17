#!/bin/bash

# Intelligent Knowledge Platform Setup Script
# This script helps you set up the development environment

set -e

echo "🚀 Intelligent Knowledge Platform Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/en/download/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.10+ first."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE="16.0.0"

if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE" ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Node.js $NODE_VERSION found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp config.env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Check if DeepSeek API key is set
if ! grep -q "DEEPSEEK_API_KEY=sk-" .env 2>/dev/null; then
    echo ""
    echo "⚠️  IMPORTANT: You need to set your DeepSeek API key!"
    echo "   1. Go to: https://platform.deepseek.com/"
    echo "   2. Create an account and get your API key"
    echo "   3. Edit .env file and set: DEEPSEEK_API_KEY=your_actual_key_here"
    echo ""
    read -p "Press Enter to continue after setting your API key..."
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Check if Docker Compose is available
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo "✅ Docker Compose found"
        echo ""
        echo "🐳 You can start the infrastructure services with:"
        echo "   docker-compose up -d"
        echo ""
    else
        echo "⚠️  Docker Compose not found. You'll need to install databases manually."
    fi
else
    echo "⚠️  Docker not found. You'll need to install databases manually."
    echo "   See DEPLOYMENT.md for manual installation instructions."
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

# Create data directory
mkdir -p data
echo "✅ Data directory created"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🔍 Running environment validation..."
source venv/bin/activate
python validate_env.py
VALIDATION_EXIT_CODE=$?

echo ""
if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    echo "✅ Environment validation passed!"
else
    echo "⚠️  Environment validation found issues. Please review the results above."
fi

echo ""
echo "📋 Next steps:"
echo "1. Make sure your .env file has the correct DEEPSEEK_API_KEY"
echo "2. Start infrastructure services:"
echo "   - With Docker: docker-compose up -d"
echo "   - Manually: See DEPLOYMENT.md for individual service setup"
echo "3. Start the platform:"
echo "   - Backend: python run_local.py"
echo "   - Frontend: cd frontend && npm run dev"
echo "4. Open browser: http://localhost:3000 in your browser"
echo ""
echo "🔧 Validate environment anytime: python validate_env.py"
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo "🆘 For help, visit: https://github.com/suleman-dawood/intelligent-knowledge-platform" 