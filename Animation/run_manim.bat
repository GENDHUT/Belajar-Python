@echo off
REM 
call venv-manimgl\Scripts\activate

REM 
manim -p -ql Animation.py HelloWorld

pause
