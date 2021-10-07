@echo off
setlocal

rem Clear any user set ERRORLEVEL variable:
set "ERRORLEVEL="

rem Enable advanced batch file commands:
verify argument_to_enforce_error 2>nul
setlocal EnableExtensions
if ERRORLEVEL 1 (
	echo=SCRIPT ABORTED: Command extensions not supported.
	exit /b 1
)
verify argument_to_enforce_error 2>nul
setlocal EnableDelayedExpansion
if ERRORLEVEL 1 (
	endlocal rem Undo "setlocal EnableExtensions"
	echo=SCRIPT ABORTED: Delayed expansion not supported.
	exit /b 1
)

rem Unset ALL environment variables except SYSTEMROOT (which is required by embedded Python):
for /f "tokens=1* delims==" %%a in ('set') do (
	if %%a NEQ "SYSTEMROOT" (
		set %% %%a=
	)
)

set "SCRIP_DIR=%~dp0"
set "SCRIP_DIR=%SCRIP_DIR:~0,-1%"

rem **************************************************************** Cleanup Python environment and call eFMI Compliance Manager:

set "PATH=%SCRIP_DIR%\python;%SCRIP_DIR%\libraries;%SCRIP_DIR%\sources"
set "PYTHONPATH=%SCRIP_DIR%\python;%SCRIP_DIR%\libraries;%SCRIP_DIR%\sources"
set "PYTHONHOME=%SCRIP_DIR%\python;%SCRIP_DIR%\libraries;%SCRIP_DIR%\sources"

set argCount=0
for %%x in (%*) do (
	set /A argCount+=1
	set "argVec[!argCount!]=%%~x"
)
if "%argCount%" NEQ "1" (
	echo=
	echo=ERROR: Unexpected number of arguments; expected a single argument, the eFMU to check.
	echo=
	exit 1
)

for /L %%i in (1,1,%argCount%) do (
	"%SCRIP_DIR%\python\python.exe" "%SCRIP_DIR%\sources\main.py" "!argVec[%%i]!"
	exit %ERRORLEVEL%
)
