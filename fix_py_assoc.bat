@echo off
echo Have you run this as an administrator?
ftype Python.File="C:\Python354x64\python.exe" "%1" %*
pause