@echo off
REM Luminote Development Environment Setup Script
REM For Windows systems
REM This script sets up the complete development environment for Luminote

setlocal enabledelayedexpansion

REM Color codes are limited in Windows batch, using simple output instead
set "CHECK_MARK=[OK]"
set "CROSS_MARK=[ERROR]"
set "WARNING_MARK=[WARNING]"
set "INFO_MARK=[INFO]"

echo.
echo ===================================================
echo Luminote Development Environment Setup
echo ===================================================
echo.

REM Step 1: Check prerequisites
echo ===================================================
echo Step 1: Checking Prerequisites
echo ===================================================
echo.

REM Check Python version
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% Python is not installed
    echo Please install Python 3.12 or higher from https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %INFO_MARK% Found Python %PYTHON_VERSION%

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% lss 3 (
    echo %CROSS_MARK% Python 3.12+ is required, but found %PYTHON_VERSION%
    echo Please upgrade Python from https://www.python.org/downloads/
    exit /b 1
)

if %PYTHON_MAJOR% equ 3 (
    if %PYTHON_MINOR% lss 12 (
        echo %CROSS_MARK% Python 3.12+ is required, but found %PYTHON_VERSION%
        echo Please upgrade Python from https://www.python.org/downloads/
        exit /b 1
    )
)
echo %CHECK_MARK% Python version check passed

REM Check Node.js version
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% Node.js is not installed
    echo Please install Node.js 22+ from https://nodejs.org/
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION_RAW=%%i
set NODE_VERSION=%NODE_VERSION_RAW:~1%
echo %INFO_MARK% Found Node.js v%NODE_VERSION%

REM Extract major version
for /f "tokens=1 delims=." %%a in ("%NODE_VERSION%") do set NODE_MAJOR=%%a

if %NODE_MAJOR% lss 22 (
    echo %CROSS_MARK% Node.js 22+ is required, but found v%NODE_VERSION%
    echo Please upgrade Node.js from https://nodejs.org/
    exit /b 1
)
echo %CHECK_MARK% Node.js version check passed

REM Check npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% npm is not installed
    echo Please install npm (usually comes with Node.js)
    exit /b 1
)
echo %CHECK_MARK% npm is available

REM Step 2: Backend setup
echo.
echo ===================================================
echo Step 2: Setting Up Backend
echo ===================================================
echo.

cd backend
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% backend directory not found
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo %INFO_MARK% Creating Python virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo %CROSS_MARK% Failed to create virtual environment
        exit /b 1
    )
    echo %CHECK_MARK% Virtual environment created
) else (
    echo %WARNING_MARK% Virtual environment already exists, skipping creation
)

REM Activate virtual environment
echo %INFO_MARK% Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% Failed to activate virtual environment
    exit /b 1
)
echo %CHECK_MARK% Virtual environment activated

REM Upgrade pip
echo %INFO_MARK% Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo %CHECK_MARK% pip upgraded

REM Install backend dependencies
echo %INFO_MARK% Installing backend dependencies...
if exist "pyproject.toml" (
    REM Try to install with uv first (faster), fall back to pip
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo %INFO_MARK% Using uv for dependency installation (faster)...
        uv pip install -e ".[dev]"
    ) else (
        echo %INFO_MARK% Using pip for dependency installation...
        pip install -e ".[dev]"
    )
) else if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo %CROSS_MARK% No dependency file found (requirements.txt or pyproject.toml)
    exit /b 1
)
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% Failed to install backend dependencies
    exit /b 1
)
echo %CHECK_MARK% Backend dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo %INFO_MARK% Creating .env file from .env.example...
        copy .env.example .env >nul
        echo %CHECK_MARK% .env file created
        echo %WARNING_MARK% Please edit backend\.env and configure your API keys
    ) else (
        echo %WARNING_MARK% No .env.example file found, skipping .env creation
    )
) else (
    echo %WARNING_MARK% .env file already exists, skipping creation
)

cd ..

REM Step 3: Frontend setup
echo.
echo ===================================================
echo Step 3: Setting Up Frontend
echo ===================================================
echo.

cd frontend
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% frontend directory not found
    exit /b 1
)

REM Install frontend dependencies
echo %INFO_MARK% Installing frontend dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo %CROSS_MARK% Failed to install frontend dependencies
    exit /b 1
)
echo %CHECK_MARK% Frontend dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo %INFO_MARK% Creating .env file from .env.example...
        copy .env.example .env >nul
        echo %CHECK_MARK% .env file created
    ) else (
        echo %WARNING_MARK% No .env.example file found, skipping .env creation
    )
) else (
    echo %WARNING_MARK% .env file already exists, skipping creation
)

cd ..

REM Step 4: Install pre-commit hooks
echo.
echo ===================================================
echo Step 4: Installing Pre-commit Hooks
echo ===================================================
echo.

REM Install pre-commit if not already installed
where pre-commit >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %INFO_MARK% Installing pre-commit...
    cd backend
    call .venv\Scripts\activate.bat
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        uv pip install pre-commit
    ) else (
        pip install pre-commit
    )
    if %ERRORLEVEL% neq 0 (
        echo %CROSS_MARK% Failed to install pre-commit
        exit /b 1
    )
    cd ..
    echo %CHECK_MARK% pre-commit installed
) else (
    echo %CHECK_MARK% pre-commit already installed
)

REM Install pre-commit hooks
echo %INFO_MARK% Installing pre-commit hooks...
cd backend
call .venv\Scripts\activate.bat
pre-commit install
if %ERRORLEVEL% neq 0 (
    echo %WARNING_MARK% Failed to install pre-commit hooks
) else (
    echo %CHECK_MARK% Pre-commit hooks installed
)
cd ..

REM Step 5: Verify setup
echo.
echo ===================================================
echo Step 5: Verifying Setup
echo ===================================================
echo.

REM Test backend
echo %INFO_MARK% Testing backend setup...
cd backend
call .venv\Scripts\activate.bat

REM Check if pytest is available
python -c "import pytest" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    REM Just check that tests can be collected (don't run them)
    pytest --collect-only -q >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo %CHECK_MARK% Backend tests can be collected successfully
    ) else (
        echo %WARNING_MARK% Backend test collection had issues (this might be expected)
    )
) else (
    echo %WARNING_MARK% pytest not installed, skipping backend test verification
)

cd ..

REM Test frontend
echo %INFO_MARK% Testing frontend setup...
cd frontend

REM Check that the npm test command is resolvable (basic check, don't run tests)
npm run test -- --help >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %CHECK_MARK% Frontend test environment is ready
) else (
    echo %WARNING_MARK% Frontend test command check had issues
)

cd ..

REM Final success message
echo.
echo ===================================================
echo Setup Complete!
echo ===================================================
echo.
echo %CHECK_MARK% Development environment setup completed successfully!
echo.
echo Next steps:
echo.
echo 1. Configure your API keys in backend\.env
echo.
echo 2. Start the backend server:
echo    cd backend ^&^& .venv\Scripts\activate.bat ^&^& luminote serve
echo.
echo 3. In a new terminal, start the frontend:
echo    cd frontend ^&^& npm run dev
echo.
echo 4. Visit http://localhost:5000 to see Luminote in action
echo.
echo For more information, see CONTRIBUTING.md
echo.

endlocal
