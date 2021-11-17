@ECHO off
SETLOCAL

REM Mayaバージョン
SET MAYAVER=2022

SET THISDIR=%~dp0
SET SITE_PACKAGES=%THISDIR%\..\site-packages\cp37-cp37m-win_amd64

SET PYTHONPATH=%THISDIR%\..;%SITE_PACKAGES%;%PYTHONPATH%
SET SSL_CERT_FILE="%SITE_PACKAGES%\certifi\cacert.pem"

REM 英語設定
SET MAYA_UI_LANGUAGE=en_US

REM Mayaを直接起動
SET MAYA_EXE=%PROGRAMFILES%\Autodesk\Maya%MAYAVER%\bin\maya.exe
IF EXIST "%MAYA_EXE%" (
    ECHO "%MAYA_EXE%" %*
    "%MAYA_EXE%" %*
    EXIT /b
)

ECHO Mayaが見つかりません。インストールおよびプラグインのセットアップを行なってください。
EXIT /b 1
