@echo off
rem use  --verbose for more output

echo.
IF "%~1"=="" GOTO endparse


echo Working for folders ...:

IF NOT [%1] == [] (
	echo %1
	autopep8 %1 --recursive --in-place --pep8-passes 100
	)
	
IF NOT [%2] == [] (
	echo %2
	autopep8 %2 --recursive --in-place --pep8-passes 100
	)
	
IF NOT [%3] == [] (
	echo %3
	autopep8 %3 --recursive --in-place --pep8-passes 100
	)

IF NOT [%4] == [] (
	echo %4
	autopep8 %4 --recursive --in-place --pep8-passes 100
	)

IF NOT [%5] == [] (
	echo %5
	autopep8 %5 --recursive --in-place --pep8-passes 100
	)

IF NOT [%6] == [] (
	echo %6
	autopep8 %6 --recursive --in-place --pep8-passes 100
	)

IF NOT [%7] == [] (
	echo %7
	autopep8 %7 --recursive --in-place --pep8-passes 100
	)

IF NOT [%8] == [] (
	echo %8
	autopep8 %8 --recursive --in-place --pep8-passes 100
	)

IF NOT [%9] == [] (
	echo %9
	autopep8 %9 --recursive --in-place --pep8-passes 100
	)
echo Finished
exit

:endparse
echo No folder arguments. Folders should be in unix format (eg. c:/temp/mydir)