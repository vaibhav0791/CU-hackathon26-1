@echo off
echo Restarting Frontend Server...
echo.
echo Step 1: Stop any running frontend servers (Ctrl+C in the terminal)
echo Step 2: Delete node_modules/.cache folder
echo Step 3: Restart with npm start
echo.
cd frontend
if exist "node_modules\.cache" (
    echo Deleting cache...
    rmdir /s /q "node_modules\.cache"
    echo Cache deleted!
) else (
    echo No cache found.
)
echo.
echo Now run: npm start
echo.
pause
