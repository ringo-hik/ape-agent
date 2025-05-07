@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo APE (Agentic Pipeline Engine) Setup Script
echo ========================================================

REM Set execution policy to bypass for this script
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" >nul 2>&1

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and try again.
    exit /b 1
)

REM Check Python version (need 3.8+)
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo Found Python !PYTHON_VERSION!

REM Create virtual environment if it doesn't exist
if not exist ape_venv (
    echo Creating virtual environment 'ape_venv'...
    python -m venv ape_venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        echo Please ensure you have Python venv module available.
        exit /b 1
    )
) else (
    echo Virtual environment 'ape_venv' already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call ape_venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to upgrade pip. Continuing with existing version.
)

REM ========== NETWORK CONFIGURATION ==========
echo.
echo ========================================================
echo Setting up environment...
echo ========================================================

REM Try to use internal PyPI mirror if available
set INTERNAL_INDEX=--index-url http://pypi.internal.company/simple/ --trusted-host pypi.internal.company
echo Checking internal PyPI mirror...
pip install %INTERNAL_INDEX% setuptools -q
if %ERRORLEVEL% NEQ 0 (
    echo Internal PyPI mirror not available, using default PyPI.
    set INTERNAL_INDEX=
) else (
    echo Successfully connected to internal PyPI mirror.
)

REM Install dependencies with retry logic
echo Installing dependencies...
call :install_requirements
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies. Please check your network connection.
    exit /b 1
)

REM Adding fixed config.py functions if needed
echo Checking config.py for required functions...
call :ensure_config_functions

REM Setup environment file
echo Setting up environment file...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo .env file created from template.
    ) else (
        echo Creating new .env file with internal configuration...
        (
            echo # APE Core environment file
            echo NETWORK_MODE=hybrid
            echo API_HOST=0.0.0.0
            echo API_PORT=8001
            echo API_TIMEOUT=120
            echo API_STREAM=true
            echo.
            echo # Security settings
            echo USE_SSL=false
            echo SSL_CERT=
            echo SSL_KEY=
            echo VERIFY_SSL=false
            echo.
            echo # LLM API settings - Update these with your LLM endpoints and API keys
            echo INTERNAL_LLM_ENDPOINT=http://internal-llm-service/api
            echo INTERNAL_LLM_API_KEY=your-internal-api-key
            echo OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
            echo OPENROUTER_API_KEY=your-openrouter-api-key
            echo.
            echo # Embedding model settings
            echo EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
            echo EMBEDDING_MODEL_PATH=models/all-MiniLM-L6-v2
            echo EMBEDDING_DIMENSION=384
            echo EMBEDDING_MAX_SEQ_LENGTH=512
            echo.
            echo # Vector DB settings
            echo VECTOR_DB_TYPE=chroma
            echo VECTOR_DB_PATH=data/chroma_db
            echo VECTOR_DB_COLLECTION=documents
            echo VECTOR_DB_DISTANCE_FUNC=cosine
            echo.
            echo # Document processing settings
            echo DOCUMENT_CHUNK_SIZE=1000
            echo DOCUMENT_CHUNK_OVERLAP=200
            echo.
            echo # Search settings
            echo SEARCH_DEFAULT_TOP_K=3
            echo SEARCH_MIN_RELEVANCE_SCORE=0.6
        ) > .env
        echo New .env file created.
    )
) else (
    echo .env file already exists.
)

REM Create necessary directories
echo Creating necessary directories...
if not exist data mkdir data
if not exist data\docs mkdir data\docs
if not exist data\chroma_db mkdir data\chroma_db
if not exist models mkdir models

REM Note about embedding models
echo NOTE: Embedding models should be manually installed in the models directory
echo Models path: models/all-MiniLM-L6-v2

REM Test run
echo Running quick test...
python -c "from src.core.config import load_config; print('Config module loaded successfully'); from src.core.network_manager import network_manager; print(f'Network manager initialized. Mode: {network_manager.current_mode}')"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Quick test failed. Please check the error message above.
) else (
    echo Quick test passed successfully!
)

echo.
echo ========================================================
echo Setup Complete!
echo ========================================================
echo.
echo To run APE Core:
echo     run_ape.bat [--internal^|--external] [--debug]
echo.
echo Note: Make sure to update your .env file with your LLM
echo endpoints and API keys before running.
echo ========================================================

REM Deactivate virtual environment
call ape_venv\Scripts\deactivate.bat
exit /b 0

REM ========== HELPER FUNCTIONS ==========

:install_requirements
echo Installing dependencies from requirements.txt...
pip install %INTERNAL_INDEX% -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Retrying installation from requirements.txt without index...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install dependencies from requirements.txt.
        exit /b 1
    )
)

REM Special handling for PyTorch - use an available version rather than strict requirements
echo Installing PyTorch...
pip install %INTERNAL_INDEX% torch
if %ERRORLEVEL% NEQ 0 (
    echo Retrying PyTorch installation...
    pip install torch
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Failed to install PyTorch. Some functionality may not work correctly.
    ) else (
        echo PyTorch installed successfully on retry.
    )
) else (
    echo PyTorch installed successfully.
)

REM Ensure chromadb is installed
echo Installing vector database libraries...
pip install %INTERNAL_INDEX% chromadb
if %ERRORLEVEL% NEQ 0 (
    echo Retrying chromadb installation...
    pip install chromadb
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Failed to install chromadb. RAG functionality may be limited.
    ) else (
        echo chromadb installed successfully on retry.
    )
) else (
    echo chromadb installed successfully.
)

REM Ensure sentence-transformers is installed
pip install %INTERNAL_INDEX% sentence-transformers
if %ERRORLEVEL% NEQ 0 (
    echo Retrying sentence-transformers installation...
    pip install sentence-transformers
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Failed to install sentence-transformers. Embedding functionality may be limited.
    ) else (
        echo sentence-transformers installed successfully on retry.
    )
) else (
    echo sentence-transformers installed successfully.
)

echo All dependencies installed successfully.
exit /b 0

:ensure_config_functions
echo Checking for required functions in src\core\config.py...
python -c "from src.core.config import get_model_config, get_available_models, get_default_model, set_default_model; print('All required functions present in config.py')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Adding required functions to config.py...
    (
        echo.
        echo def get_model_config(model_key: str) -> Dict[str, Any]:
        echo     """Get model configuration"""
        echo     from src.core.network_manager import network_manager
        echo     return network_manager.get_model_config(model_key)
        echo.
        echo def get_available_models() -> List[str]:
        echo     """Get list of available model keys"""
        echo     from src.core.network_manager import network_manager
        echo     return network_manager.get_available_model_keys()
        echo.
        echo def get_default_model() -> str:
        echo     """Get default model key based on current network mode"""
        echo     from src.core.network_manager import network_manager
        echo     return network_manager.get_default_model_key()
        echo.
        echo def set_default_model(model_key: str) -> None:
        echo     """Update default model setting"""
        echo     # Currently not implemented
        echo     # Will be implemented if needed in the future
        echo     pass
    ) >> src\core\config.py
    echo Required functions added to config.py
) else (
    echo All required functions are already present in config.py
)
exit /b 0