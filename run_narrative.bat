@echo off
call .venv\Scripts\activate.bat
python test_narrative_mode.py > out_narrative.txt 2>&1
echo Done running narrative mode test
