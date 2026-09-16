@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r environment\requirements.txt
python python\17_ai_pricing_contract_scenarios.py %*
