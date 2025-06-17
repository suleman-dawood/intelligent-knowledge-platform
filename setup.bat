@echo off

REM Intelligent Knowledge Platform Setup Script for Windows
REM This script helps you set up the development environment

echo 🚀 Intelligent Knowledge Platform Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    echo    Download from: https://nodejs.org/en/download/
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy config.env.example .env
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

REM Check if DeepSeek API key is set
findstr /C:"DEEPSEEK_API_KEY=sk-" .env >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  IMPORTANT: You need to set your DeepSeek API key!
    echo    1. Go to: https://platform.deepseek.com/
    echo    2. Create an account and get your API key
    echo    3. Edit .env file and set: DEEPSEEK_API_KEY=your_actual_key_here
    echo.
    pause
)

REM Create virtual environment
if not exist venv (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Python dependencies installed

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
cd ..
echo ✅ Frontend dependencies installed

REM Check if Docker is available
docker --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Docker found
    
    REM Check if Docker Compose is available
    docker-compose --version >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Docker Compose found
        echo.
        echo 🐳 You can start the infrastructure services with:
        echo    docker-compose up -d
        echo.
    ) else (
        echo ⚠️  Docker Compose not found. You'll need to install databases manually.
    )
) else (
    echo ⚠️  Docker not found. You'll need to install databases manually.
    echo    See DEPLOYMENT.md for manual installation instructions.
)

REM Create logs directory
if not exist logs mkdir logs
echo ✅ Logs directory created

REM Create data directory
if not exist data mkdir data
echo ✅ Data directory created

echo.
echo 🎉 Setup completed successfully!
echo.
echo 🔍 Running environment validation...
call venv\Scripts\activate
python validate_env.py
set VALIDATION_EXIT_CODE=%ERRORLEVEL%

echo.
if %VALIDATION_EXIT_CODE% EQU 0 (
    echo ✅ Environment validation passed!
) else (
    echo ⚠️  Environment validation found issues. Please review the results above.
)

echo.
echo 📋 Next steps:
echo 1. Make sure your .env file has the correct DEEPSEEK_API_KEY
echo 2. Start infrastructure services:
echo    - With Docker: docker-compose up -d
echo    - Manually: See DEPLOYMENT.md for individual service setup
echo 3. Start the platform:
echo    - Backend: python run_local.py
echo    - Frontend: cd frontend ^&^& npm run dev
echo 4. Open browser: http://localhost:3000 in your browser
echo.
echo 🔧 Validate environment anytime: python validate_env.py
echo 📖 For detailed instructions, see DEPLOYMENT.md
echo 🆘 For help, visit: https://github.com/suleman-dawood/intelligent-knowledge-platform

pause 