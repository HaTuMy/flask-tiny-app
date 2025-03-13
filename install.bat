@echo off
echo Setting up a virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Running flask app...
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause
