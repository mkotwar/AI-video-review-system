@echo off
call .venv\Scripts\activate.bat
python validate_12_3.py > validate_12_3_out.txt 2>&1
echo Done running validation
