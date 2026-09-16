@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r environment\requirements.txt
python python\02_descriptive_statistics_and_visuals.py %*
