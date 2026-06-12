@echo off
cd /d "c:\Mukul K\vinfo1\video-search-engine"
call .venv\Scripts\activate.bat
python print_traceback.py > traceback_output.txt 2>&1
