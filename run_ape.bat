@echo off
REM APE (Agentic Pipeline Engine) Run Script
REM Version 1.1

setlocal EnableDelayedExpansion

REM Default settings
set MODE=internal
set DEBUG=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if /i "%~1"=="--internal" (
    set MODE=internal
    shift
    goto :parse_args
)
if /i "%~1"=="--external" (
    set MODE=external
    shift
    goto :parse_args
)
if /i "%~1"=="--debug" (
    set DEBUG=true
    shift
    goto :parse_args
)
echo Unknown option: %1
echo Usage: %0 [--internal^|--external] [--debug]
exit /b 1
:end_parse

REM Display current mode
echo.
echo ========================================================
echo Running APE (Agentic Pipeline Engine) - %MODE% mode
if "%DEBUG%"=="true" echo Debug: Enabled
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    exit /b 1
)

REM Check if virtual environment exists
if not exist ape_venv (
    echo Error: Virtual environment not found.
    echo Run setup.bat first to configure the environment.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ape_venv\Scripts\activate.bat

REM Create PID file to help with process management
set PID_FILE=server.pid
echo Creating PID file...
echo %date% %time% > %PID_FILE%

REM Set up log file
set LOGFILE=ape_server.log
echo Starting server, logging to %LOGFILE%

REM Create log header
echo ======================================================== > %LOGFILE%
echo APE Core Server Started: %DATE% %TIME% >> %LOGFILE%
echo Network Mode: %MODE% >> %LOGFILE%
echo Debug Mode: %DEBUG% >> %LOGFILE%
echo ======================================================== >> %LOGFILE%
echo. >> %LOGFILE%

REM Run with appropriate parameters
if "%DEBUG%"=="true" (
    echo Debug mode enabled. Detailed logs will be displayed.
    python run.py --mode %MODE% --debug
) else (
    echo Normal mode. Server is starting...
    
    REM Try to use PowerShell for better output handling if available
    powershell -Command "& {python run.py --mode %MODE% 2>&1 | Tee-Object -FilePath '%LOGFILE%' -Append}" >nul 2>&1
    
    if %ERRORLEVEL% NEQ 0 (
        REM Fallback if PowerShell is not available or fails
        echo Falling back to standard output...
        python run.py --mode %MODE% 2>> %LOGFILE%
    )
)

REM Remove PID file when server stops
if exist %PID_FILE% del %PID_FILE%

REM Deactivate virtual environment
call ape_venv\Scripts\deactivate.bat

echo.
echo APE Core server has been stopped.
echo.

endlocal