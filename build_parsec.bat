@echo off
echo Building ParsecCore - StarSim Physics Engine
echo ===========================================

cd /d "%~dp0"

echo Current directory: %CD%
echo.

if not exist "int\StarSim\ParsecCore" (
    echo Error: ParsecCore directory not found at int\StarSim\ParsecCore
    pause
    exit /b 1
)

echo Navigating to ParsecCore directory...
cd int\StarSim\ParsecCore

echo.
echo Step 1: Cleaning existing build directory...
if exist build (
    echo Removing existing build directory...
    rmdir /s /q build 2>nul
    if exist build (
        echo Warning: Some files couldn't be removed. Trying force removal...
        attrib -r build\* /s 2>nul
        rmdir /s /q build 2>nul
        if exist build (
            echo Warning: Build directory still exists. Continuing anyway...
        )
    )
    echo Build directory cleanup completed
)

echo.
echo Step 2: Creating fresh build directory...
mkdir build
cd build

echo.
echo Step 3: Running CMake configuration...
echo This will download dependencies (googletest, nlohmann/json, muParser)
echo This may take several minutes on first run...
cmake .. -G "Visual Studio 17 2022"

if errorlevel 1 (
    echo.
    echo CMake configuration failed!
    echo.
    echo Common solutions:
    echo 1. Install Visual Studio 2022 with C++ development tools
    echo 2. Install CMake and ensure it's in your PATH
    echo 3. Check internet connection for dependency downloads
    echo 4. Try running as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo Step 4: Building the project...
cmake --build .

if errorlevel 1 (
    echo.
    echo Build failed!
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS: ParsecCore built successfully!
echo ============================================
echo.
echo You can now:
echo 1. Run tests: ctest
echo 2. Run examples: .\Debug\parsec_windows_app.exe
echo 3. Use HyperThreader to start StarSim integration
echo.
echo Build directory: %CD%
echo.
pause