@echo off
echo ===============================================
echo StarSim Build Script
echo ===============================================
echo.
echo This will build ParsecCore for StarSim integration
echo.
echo Current directory: %CD%
echo.
echo Step 1: Navigate to ParsecCore directory
cd int\StarSim\ParsecCore
echo.
echo Step 2: Create build directory
if exist build rmdir /s /q build
mkdir build
cd build
echo.
echo Step 3: Configure with CMake
cmake .. -G "Visual Studio 17 2022"
if errorlevel 1 (
    echo.
    echo CMake configuration failed!
    echo Make sure you have Visual Studio 2022 and CMake installed
    pause
    exit /b 1
)
echo.
echo Step 4: Build the project
cmake --build .
if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)
echo.
echo ===============================================
echo BUILD SUCCESSFUL!
echo ===============================================
echo.
echo StarSim ParsecCore has been built successfully
echo You can now use HyperThreader to start StarSim
echo.
pause
