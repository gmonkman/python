@echo off
set "p=%~dp0"
set "p=%p:\=/%"
echo %p%
C:\windows\System32\cmd.exe /k jupyter notebook --notebook-dir="%p%"
