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

rem Unset ALL environment variables:
for /f "tokens=1* delims==" %%a in ('set') do (
	if %%a NEQ "ComSpec" (
		set %% %%a=
	)
)
call :dirname "%ComSpec%" SYSTEM_DIR
set ComSpec=

set "SCRIP_DIR=%~dp0"
set "SCRIP_DIR=%SCRIP_DIR:~0,-1%"

rem ******************************************************************************** Cleanup distribution and build from sources:

rem Create temporary workfolder:
rmdir /q /s ^
	"%SCRIP_DIR%\tmp" > nul 2>&1
mkdir ^
	"%SCRIP_DIR%\tmp"

rem Create distribution directory:
rmdir /q /s ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker" > nul 2>&1
mkdir ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker"

rem Copy check script and license:
copy ^
	"%SCRIP_DIR%\check-eFMU.bat" ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker"
copy ^
	"%SCRIP_DIR%\..\..\LICENSE" ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker"

rem Copy embedded Python and create its search path configuration:
mkdir ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker\python"
pushd "%SCRIP_DIR%"
for %%f in (python-*.zip) do (
	pushd "%SCRIP_DIR%\eFMI-Compliance-Checker\python"
	"!SYSTEM_DIR!\tar.exe" ^
		-xf "!SCRIP_DIR!\%%f"
	popd
)
popd
pushd "%SCRIP_DIR%\eFMI-Compliance-Checker\python"
for %%f in (python*._pth) do (
	echo=>> "%%f"
	echo=# Add 3rd party libraries and eFMI Compliance Checker sources to search path:>> "%%f"
	echo=../libraries>> "%%f"
	echo=../sources>> "%%f"
)
popd

rem Copy 3rd party libraries:
mkdir ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker\libraries"
pushd "%SCRIP_DIR%\3rd-party-libraries"
for %%f in (*.zip) do (
	call :basename "%%f" LIBRARY_NAME_VERSIONED
	for /f "tokens=1 delims=-" %%a in ("%%f") do (
		set LIBRARY_NAME=%%a
	)
	rem Unpack library distribution:
	pushd "!SCRIP_DIR!\tmp"
	"!SYSTEM_DIR!\tar.exe" ^
		-xf "!SCRIP_DIR!\3rd-party-libraries\%%f"
	popd
	rem Copy library implementation (not whole distribution, just it's implementation):
	mkdir ^
		"!SCRIP_DIR!\eFMI-Compliance-Checker\libraries\!LIBRARY_NAME!"
	"!SYSTEM_DIR!\xcopy.exe" /e /h /k /v ^
		"!SCRIP_DIR!\tmp\!LIBRARY_NAME_VERSIONED!\!LIBRARY_NAME!" ^
		"!SCRIP_DIR!\eFMI-Compliance-Checker\libraries\!LIBRARY_NAME!"
	rem Copy library license:
	pushd "!SCRIP_DIR!\tmp\!LIBRARY_NAME_VERSIONED!"
	for %%b in (LICENSE*) do (
		copy ^
			"%%b" ^
			"!SCRIP_DIR!\eFMI-Compliance-Checker\libraries\!LIBRARY_NAME!"
	)
	popd
)
popd

rem Copy eFMI Compliance Checker implementation:
mkdir ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker\sources"
"%SYSTEM_DIR%\xcopy.exe" /e /h /k /v ^
	"%SCRIP_DIR%\..\..\complianceChecker" ^
	"%SCRIP_DIR%\eFMI-Compliance-Checker\sources"

rem Delete temporary workfolder:
rmdir /q /s ^
	"%SCRIP_DIR%\tmp" > nul 2>&1

goto :EOF

rem ********************************************************************************************************** Support functions:

:dirname file var
	setlocal
	set _dir=%~dp1
	set _dir=%_dir:~0,-1%
	endlocal & set %2=%_dir%
goto :EOF

:basename file var
	for /F "delims=" %%i in (%1) do (
		set %2=%%~ni
	)
goto :EOF
