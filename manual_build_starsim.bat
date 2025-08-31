@echo off
echo Manual ParsecCore Build
echo ======================
cd /d "C:\Users\buzza\Desktop\Projects\Active\Comms\int\StarSim\ParsecCore\build"
echo.
echo Current directory: %CD%
echo.
echo Step 1: Run CMake configuration
echo cmake .. -G "Visual Studio 17 2022"
echo.
echo Step 2: Build the project
echo cmake --build .
echo.
echo Step 3: Run tests (optional)
echo ctest
echo.
echo Press any key to start CMake configuration...
pause
cmake .. -G "Visual Studio 17 2022"
if errorlevel 1 (
    echo CMake configuration failed!
    pause
    exit /b 1
)
echo.
echo CMake configuration completed. Press any key to build...
pause
cmake --build .
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
echo.
echo Build completed successfully!
echo.
echo You can now run tests with: ctest
echo.
pause
