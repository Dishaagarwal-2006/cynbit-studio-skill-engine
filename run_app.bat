@echo off
cd /d "%~dp0"
echo ==== Cynbit Studio Skill Engine ====
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate
echo Installing requirements, please wait...
pip install -q -r requirements.txt
if not exist .env (
  copy .env.example .env >nul
  echo.
  echo Paste your GEMINI_API_KEY in the Notepad window, Save, then close Notepad.
  notepad .env
)
start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:8000"
echo Starting server. Keep this window OPEN. Press Ctrl+C to stop.
uvicorn app.main:app
pause
