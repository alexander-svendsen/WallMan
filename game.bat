# Shellscript for runnning the game for windows users

setlocal
set PYTHONPATH=%cd%;%PYTHONPATH%

#You must change the address if the master has moved
python game/main.py -a 129.242.22.192 -r 504 504
endlocal
