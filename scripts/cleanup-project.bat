@echo off
echo ========================================
echo modLRN Project Cleanup
echo ========================================
echo.

echo Cleaning up project structure...

echo.
echo Removing duplicate files...
if exist "backend\main.py" del "backend\main.py"
if exist "backend\init_badges.py" del "backend\init_badges.py"
if exist "backend\CODING_PLATFORM_STATUS.md" del "backend\CODING_PLATFORM_STATUS.md"
if exist "backend\judge0_setup.md" del "backend\judge0_setup.md"

echo.
echo Removing old startup scripts from root...
if exist "start_backend.py" del "start_backend.py"
if exist "start_server.bat" del "start_server.bat"
if exist "start_server_fixed.bat" del "start_server_fixed.bat"
if exist "start-backend.bat" del "start-backend.bat"
if exist "start-frontend.bat" del "start-frontend.bat"

echo.
echo Removing test files from root...
if exist "test_*.py" del "test_*.py"
if exist "test_*.html" del "test_*.html"

echo.
echo Removing utility files from root...
if exist "clear_and_create_admin.py" del "clear_and_create_admin.py"
if exist "create_admin_user.py" del "create_admin_user.py"
if exist "fix_admin_auth.py" del "fix_admin_auth.py"
if exist "fix_admin.py" del "fix_admin.py"
if exist "reset_admin.py" del "reset_admin.py"
if exist "reset_original_admin.py" del "reset_original_admin.py"

echo.
echo Removing documentation files from root...
if exist "*.md" del "*.md"

echo.
echo Removing package files from root...
if exist "package-lock.json" del "package-lock.json"

echo.
echo Removing src directory from root...
if exist "src" rmdir /s /q "src"

echo.
echo ========================================
echo Cleanup completed successfully!
echo.
echo Project structure is now organized:
echo - Backend: backend/
echo - Frontend: frontend/
echo - Scripts: scripts/
echo - Documentation: docs/
echo - Tests: tests/
echo ========================================
pause
