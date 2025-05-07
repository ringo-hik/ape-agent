@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo APE Core - Build Script
echo ========================================================
echo.

REM Setup variables
set OUTPUT_DIR=dist\app
set CONFIG_BACKUP=config\_backup

REM Make sure output directory exists
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Create backup directory
if not exist %CONFIG_BACKUP% mkdir %CONFIG_BACKUP%

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    exit /b 1
)

echo Creating APE Core build...
echo.

REM Step 1: Backup current environment settings
echo Step 1: Backing up current settings...
if exist .env copy .env %CONFIG_BACKUP%\.env.bak
if exist .env.example copy .env.example %CONFIG_BACKUP%\.env.example.bak

REM Step 2: Set up environment file
echo Step 2: Setting up environment file...
if exist .env.example (
    copy .env.example .env
    echo Environment file created from template.
) else (
    echo Error: .env.example not found!
    echo Please make sure .env.example exists before building.
    exit /b 1
)

REM Step 3: Run the setup script
echo Step 3: Running setup script...
call setup.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error: Setup script failed.
    exit /b 1
)

REM Step 4: Copy files to distribution folder
echo Step 4: Copying files to %OUTPUT_DIR%...
xcopy /E /Y /I *.* %OUTPUT_DIR%\ /EXCLUDE:exclude_files.txt
if not exist exclude_files.txt (
    echo Creating exclude_files.txt...
    (
        echo .git\
        echo __pycache__\
        echo *.pyc
        echo dist\
        echo %CONFIG_BACKUP%\
        echo *.bak
        echo .gitignore
        echo *.log
    ) > exclude_files.txt
    xcopy /E /Y /I *.* %OUTPUT_DIR%\ /EXCLUDE:exclude_files.txt
)

REM Step 5: Clean up unnecessary files in dist
echo Step 5: Cleaning up unnecessary files in distribution...
if exist %OUTPUT_DIR%\config\_backup rmdir /S /Q %OUTPUT_DIR%\config\_backup
for /d /r %OUTPUT_DIR% %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r %OUTPUT_DIR% %%f in (*.pyc) do @if exist "%%f" del "%%f"

REM Step 6: Create a README.md for deployment
echo Step 6: Creating deployment README...
(
    echo # APE Core - Deployment Package
    echo.
    echo ## Setup and Run Instructions
    echo.
    echo 1. Extract this package to your deployment server
    echo 2. Run `setup.bat` to configure the environment
    echo 3. Edit the `.env` file with your LLM endpoints and API keys
    echo 4. Run `run_ape.bat` to start the server
    echo.
    echo ## Important Configuration
    echo.
    echo - Set the right network mode in `.env` file: `NETWORK_MODE=internal` or `NETWORK_MODE=external`
    echo - Update appropriate LLM endpoints and API keys in `.env`
    echo - Ensure embedding models are available in the models directory
    echo.
    echo ## Embedding Models
    echo.
    echo Make sure to place your embedding models in the models directory:
    echo - models/all-MiniLM-L6-v2/
    echo.
    echo ## Contact
    echo.
    echo For any issues or questions, please contact the APE team
) > %OUTPUT_DIR%\README.md

REM Step 7: Create a verification script
echo Step 7: Creating verification script...
(
    echo @echo off
    echo echo Testing APE Core installation...
    echo echo.
    echo.
    echo call ape_venv\Scripts\activate.bat
    echo.
    echo echo Testing Python configuration...
    echo python -c "from src.core.config import load_config; print('Config module loaded successfully'); from src.core.network_manager import network_manager; print(f'Network manager initialized. Mode: {network_manager.current_mode}')"
    echo.
    echo if %%ERRORLEVEL%% NEQ 0 (
    echo     echo Failed to verify installation. Please check the error above.
    echo     exit /b 1
    echo ^)
    echo.
    echo echo Checking embedding model directory...
    echo if not exist "models\all-MiniLM-L6-v2" (
    echo     echo WARNING: Embedding model directory not found.
    echo     echo Create directory: models\all-MiniLM-L6-v2
    echo     echo Copy your embedding model files to this location.
    echo ^) else (
    echo     echo Embedding model directory found.
    echo ^)
    echo.
    echo echo.
    echo echo Verification complete!
    echo echo.
    echo call ape_venv\Scripts\deactivate.bat
) > %OUTPUT_DIR%\verify_installation.bat

REM Step 8: Test the build
echo Step 8: Verifying the build...
cd %OUTPUT_DIR%
call setup.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error: Build verification failed.
    exit /b 1
)

REM Deactivate virtual environment if active
call ape_venv\Scripts\deactivate.bat 2>nul

REM Change back to root directory
cd ..\..

REM Step 9: Create a ZIP archive
echo Step 9: Creating deployment package...
powershell -Command "Compress-Archive -Path '%OUTPUT_DIR%\*' -DestinationPath 'dist\ape-core.zip' -Force"

REM Restore original environment settings
echo Restoring original environment settings...
if exist %CONFIG_BACKUP%\.env.bak copy %CONFIG_BACKUP%\.env.bak .env

echo.
echo ========================================================
echo Build complete!
echo.
echo Build output: dist\ape-core.zip
echo.
echo You can deploy this package to your servers.
echo ========================================================

endlocal