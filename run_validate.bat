@echo off
call .venv\Scripts\activate.bat
python validate_12_1.py > validate_out.txt 2>&1
echo Done running validation
