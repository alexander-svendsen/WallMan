# Shellscript for runnning the server for windows users

setlocal
set PYTHONPATH=%cd%;%PYTHONPATH%
cd server
python server.py
endlocal
