@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Purpose:
rem   Windows one-click launcher for AGENTS web dashboard.
rem Usage:
rem   start_web.bat [start_web.py args...]

set "RUNNER="

where py >nul 2>&1
if not errorlevel 1 (
  set "RUNNER=py -3"
) else (
  where python >nul 2>&1
  if not errorlevel 1 (
    set "RUNNER=python"
  )
)

if not defined RUNNER (
  echo Python runtime not found. Please install Python 3.
  exit /b 1
)

%RUNNER% start_web.py %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Start failed. Press any key to exit.
  pause >nul
)

endlocal & exit /b %EXIT_CODE%
