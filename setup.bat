@echo off
echo Setting up Driver Drowsiness Detection System...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Download shape_predictor_68_face_landmarks.dat from:
echo    http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
echo 2. Extract and place it in this directory
echo 3. Add an alarm.wav file to the static/ folder
echo 4. Run: python app.py
echo.
pause
