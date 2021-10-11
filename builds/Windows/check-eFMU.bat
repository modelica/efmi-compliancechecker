@rem Copyright (c) 2021, ESI ITI GmbH, Modelica Association and contributors
@rem 
@rem Licensed under the 3-Clause BSD license (the "License");
@rem you may not use this software except in compliance with
@rem the "License".
@rem 
@rem This software is not fully developed or tested.
@rem 
@rem THE SOFTWARE IS PROVIDED "as is", WITHOUT ANY WARRANTY
@rem of any kind, either express or implied, and the use is 
@rem completely at your own risk.
@rem 
@rem The software can be redistributed and/or modified under
@rem the terms of the "License".
@rem 
@rem See the "License" for the specific language governing
@rem permissions and limitations under the "License".

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
	echo=ERROR:   Unexpected number of arguments; expected a single argument, the eFMU-archive to check
	echo=         ^(zip file ending in *.fmu, containing an "eFMU" directory^).
	echo=WARNING: The "eFMU" directory of a given eFMU-archive will be unpacked in the current
	echo=         work directory.
	echo=
	exit /b 1
)

for /L %%i in (1,1,%argCount%) do (
	"%SCRIP_DIR%\python\python.exe" "%SCRIP_DIR%\sources\main.py" "!argVec[%%i]!"
	if ERRORLEVEL 1 (
		exit /b 1
	) else (
		exit /b 0
	)
)
