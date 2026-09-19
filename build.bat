@echo off
REM ============================================================
REM  Builds ExpenseTracker.exe (a single file, no Python needed
REM  to run it afterwards). Run this ONCE from inside this folder.
REM  Result appears in the "dist" folder as ExpenseTracker.exe
REM ============================================================

echo Installing/upgrading build tools (one-time)...
py -m pip install --upgrade pyinstaller PySide6 PySide6-Fluent-Widgets

echo.
echo Building ExpenseTracker.exe ... this can take a few minutes.
py -m PyInstaller --noconfirm --onefile --windowed ^
    --name "ExpenseTracker" ^
    --collect-all qfluentwidgets ^
    --collect-all PySide6 ^
    main.py

echo.
echo ============================================================
echo Done! Your app is at:  dist\ExpenseTracker.exe
echo Copy that one file anywhere you like (e.g. the Desktop) and
echo double-click it to run the app - no extra setup needed.
echo ============================================================
pause
