@echo off
rem Pass list of folders to pep8
rem use  --verbose for more output
if "%~1"=="" GOTO endparse
if NOT "%1" == "" autopep8 %1 --recursive --in-place --pep8-passes 100
if NOT "%2" == "" autopep8 %2 --recursive --in-place --pep8-passes 100
if NOT "%3" == "" autopep8 %3 --recursive --in-place --pep8-passes 100
if NOT "%4" == "" autopep8 %4 --recursive --in-place --pep8-passes 100
if NOT "%5" == "" autopep8 %5 --recursive --in-place --pep8-passes 100
if NOT "%6" == "" autopep8 %6 --recursive --in-place --pep8-passes 100
if NOT "%7" == "" autopep8 %7 --recursive --in-place --pep8-passes 100
if NOT "%8" == "" autopep8 %8 --recursive --in-place --pep8-passes 100
if NOT "%9" == "" autopep8 %9 --recursive --in-place --pep8-passes 100
:endparse
pause
exit
echo No folder arguments. Folders should be in unix format (eg. c:/temp/mydir)
pause