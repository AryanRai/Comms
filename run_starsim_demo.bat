@echo off
echo ===============================================
echo StarSim Integration Demo
echo ===============================================
echo.
echo Starting StarSim-Comms integration demo...
echo.
echo Current directory: %CD%
echo.
cd int\StarSim
echo Changed to StarSim directory: %CD%
echo.
echo Running integration demo...
python run_integration_demo.py
echo.
echo Demo finished. Press any key to close...
pause
