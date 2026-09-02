@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r environment\requirements.txt
python python\36_circular_economy_material_carbon_cost.py %*
