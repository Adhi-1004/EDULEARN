@echo off
echo Starting modLRN Frontend Development Server...
echo.

echo Installing/updating dependencies...
npm install

echo.
echo Starting Vite development server on http://localhost:5173
echo Press Ctrl+C to stop the server
echo.

npm run dev
