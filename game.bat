# Shellscript for runnning the game for windows users

setlocal
set PYTHONPATH=%cd%;%PYTHONPATH%
python gamelogic/main.py -a 129.242.22.192  #You must change the address if the master has moved
endlocal
