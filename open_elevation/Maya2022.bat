@ECHO off
SETLOCAL

REM Maya�o�[�W����
SET MAYAVER=2022

SET THISDIR=%~dp0
SET SITE_PACKAGES=%THISDIR%\..\site-packages\cp37-cp37m-win_amd64

SET PYTHONPATH=%THISDIR%\..;%SITE_PACKAGES%;%PYTHONPATH%
SET SSL_CERT_FILE="%SITE_PACKAGES%\certifi\cacert.pem"

REM �p��ݒ�
SET MAYA_UI_LANGUAGE=en_US

REM Maya�𒼐ڋN��
SET MAYA_EXE=%PROGRAMFILES%\Autodesk\Maya%MAYAVER%\bin\maya.exe
IF EXIST "%MAYA_EXE%" (
    ECHO "%MAYA_EXE%" %*
    "%MAYA_EXE%" %*
    EXIT /b
)

ECHO Maya��������܂���B�C���X�g�[������уv���O�C���̃Z�b�g�A�b�v���s�Ȃ��Ă��������B
EXIT /b 1
