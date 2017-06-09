@echo off
rem use --verbose for more output

echo.
IF "%~1" == "" GOTO endparse


echo Working for folders ...:
pause
IF NOT [%1] == [] (
    echo % 1
	pause
    autopep8 %1 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
	pause
)

IF NOT [%2] == [] (
    echo % 2
    autopep8 %2 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%3] == [] (
    echo % 3
    autopep8 %3 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%4] == [] (
    echo % 4
    autopep8 %4 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%5] == [] (
    echo % 5
    autopep8 %5 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%6] == [] (
    echo % 6
    autopep8 %6 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%7] == [] (
    echo % 7
    autopep8 %7 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%8] == [] (
    echo % 8
    autopep8 %8 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)

IF NOT [%9] == [] (
    echo % 9
    autopep8 %9 --in-place --exclude=*.bat,*.cmd,*.txt,*.ini,*.cfg --pep8-passes 100
)
echo Finished
exit

: endparse
echo No folder arguments. Folders should be in unix format(eg. c: / temp / mydir)
