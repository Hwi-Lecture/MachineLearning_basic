@echo off
REM ============================================================
REM  Double-click this file to install everything needed for
REM  the class: Python, VS Code, PATH setup, requirements.txt.
REM
REM  NOTE: Run THIS file (setup.bat). Do not run setup.ps1
REM  directly - Windows security settings will block it.
REM
REM  (Korean messages are shown by setup.ps1, not here, to
REM  avoid cmd.exe's Korean text encoding bug.)
REM ============================================================

echo Starting setup...
echo When the admin permission (UAC) prompt appears, click Yes.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

echo.
echo ====================================================
echo  This is the setup.bat window.
echo  Actual installation runs in a NEW (Administrator)
echo  PowerShell window - check progress there.
echo ====================================================
pause
