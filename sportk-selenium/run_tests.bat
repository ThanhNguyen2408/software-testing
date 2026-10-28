@echo off
REM Chạy: run_tests.bat   (cần mock-server cổng 3001 và frontend cổng 3000 đang chạy)
set BROWSER=chrome
python -m pytest %*
