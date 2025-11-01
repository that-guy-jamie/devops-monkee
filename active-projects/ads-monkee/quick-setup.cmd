@echo off
REM Ads Monkee - Quick Setup Script
REM This installs dependencies, runs migrations, seeds clients, and starts migration

echo ================================================================================
echo ADS MONKEE - QUICK SETUP
echo ================================================================================
echo.

cd /d "%~dp0"

echo [1/6] Installing Poetry dependencies (this may take 2-3 minutes)...
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe install
if errorlevel 1 (
    echo ERROR: Poetry install failed
    pause
    exit /b 1
)
echo     DONE!
echo.

echo [2/6] Generating Alembic migration...
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe run alembic revision --autogenerate -m "Initial schema - 17 tables"
if errorlevel 1 (
    echo ERROR: Migration generation failed
    pause
    exit /b 1
)
echo     DONE!
echo.

echo [3/6] Applying migrations to database...
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe run alembic upgrade head
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)
echo     DONE!
echo.

echo [4/6] Seeding clients from Google Ads API...
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe run python scripts/seed_clients.py
if errorlevel 1 (
    echo ERROR: Client seeding failed
    pause
    exit /b 1
)
echo     DONE!
echo.

echo [5/6] Verifying database setup...
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe run python -c "from backend.database import SessionLocal; from backend.models import Client; s = SessionLocal(); count = s.query(Client).count(); print(f'Clients in database: {count}'); s.close()"
echo     DONE!
echo.

echo [6/6] Starting data migration (30-45 minutes)...
echo.
echo     This will pull 1 year of data for all 30 clients:
echo     - Campaigns
echo     - Ad Groups
echo     - Keywords
echo     - Search Terms
echo.
echo     Progress will be shown in real-time.
echo     You can walk away - it will run to completion.
echo.
pause
echo.
C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe run python scripts/migrate_all_clients_data.py
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS! ADS MONKEE DATA MIGRATION COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Verify data: poetry run python -c "from backend.database import SessionLocal; from backend.models import GoogleAdsCampaign; s = SessionLocal(); print(f'Campaigns: {s.query(GoogleAdsCampaign).count():,}'); s.close()"
echo   2. Start API: poetry run uvicorn backend.main:app --reload
echo   3. Test health: curl http://localhost:8000/health
echo.
pause

