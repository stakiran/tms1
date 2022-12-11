@echo off
setlocal

set mydir=%~dp0
set input_folder=scb
set output_folder=html_debugout

python dobu.py --input-directory %mydir%%input_folder% --output-directory %mydir%%output_folder%

set NO_OVERWRITE_CONFIRM=/Y
xcopy %mydir%stylesheet.css %mydir%%output_folder% %NO_OVERWRITE_CONFIRM%
