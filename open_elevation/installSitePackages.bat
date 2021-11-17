@ECHO OFF
SETLOCAL

SET THISDIR=%~dp0

SET VENV_BASE_DIR=%USERPROFILE%\.virtualenvs
SET VENV_NAME=venv_open_elevation

SET SITE_PACKAGES_DIR=%THISDIR%\..\site-packages\cp37-cp37m-win_amd64

if not exist %VENV_BASE_DIR% (
  ECHO MKDIR %VENV_BASE_DIR%
  MKDIR %VENV_BASE_DIR%
)

ECHO "py -3.7 -m venv %VENV_BASE_DIR%\%VENV_NAME%"
py -3.7 -m venv "%VENV_BASE_DIR%\%VENV_NAME%"

ECHO "activate venv..."
CALL "%VENV_BASE_DIR%\%VENV_NAME%\Scripts\activate.bat"

python -m pip install --upgrade pip
python -m pip install --upgrade -r "%THISDIR%\requirements.txt"

ECHO "deactivate venv..."
CALL deactivate

py -3.7 copy_site_packages.py ^
  --source "%VENV_BASE_DIR%\%VENV_NAME%\Lib\site-packages" ^
  --dest "%SITE_PACKAGES_DIR%"
