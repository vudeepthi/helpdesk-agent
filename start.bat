@echo off
echo Starting IT Helpdesk App...

echo Installing frontend dependencies...
cd client
call npm install
cd ..

echo Starting backend...
start "Helpdesk Backend" cmd /k "cd server && uv run python main.py"

echo Starting frontend...
start "Helpdesk Frontend" cmd /k "cd client && npm run dev"

timeout /t 5 /nobreak >nul

echo Opening browser...
start http://localhost:3001

echo Done! App running at http://localhost:3001 (or 3002 if 3001 is in use)
echo Backend running at http://localhost:8003
