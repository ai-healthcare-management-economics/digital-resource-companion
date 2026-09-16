@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r environment\requirements.txt
python python\03_missing_data_sensitivity.py %*
