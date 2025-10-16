@echo off
echo 🚀 Iniciando entorno virtual para Proyecto Aurelion...
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Instalación completa. Ejecutá:
echo python proyecto_aurelion.py
pause
