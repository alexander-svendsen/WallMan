<pre>
=======================================================================
*   __      __            ___    ___                                  *
*  /\ \  __/\ \          /\_ \  /\_ \    /'\_/`\                      *
*  \ \ \/\ \ \ \     __  \//\ \ \//\ \  /\      \     __      ___     *
*   \ \ \ \ \ \ \  /'__`\  \ \ \  \ \ \ \ \ \__\ \  /'__`\  /' _ `\   *
*    \ \ \_/ \_\ \/\ \_\.\_ \_\ \_ \_\ \_\ \ \_/\ \/\ \_\.\_/\ \/\ \  *
*     \ `\___ ___/\ \__/.\_\/\____\/\____\\ \_\\ \_\ \__/.\_\ \_\ \_\ *
*      '\/__//__/  \/__/\/_/\/____/\/____/ \/_/ \/_/\/__/\/_/\/_/\/_/ *
=======================================================================
</pre>
=======================================================================
A distributed Wall-Man game made for distributed walls.

Heavenly inspired by pac-man. More rules will follow.

## What
Welcome to the WallMan game

TODO

## Requirements
- python 2.7.3 - http://www.python.org/
- pygame 1.9.3 - http://www.pygame.org/

## How to use
- Run the server by using the server.sh for linux users or serber.bat for windows users.
There is a need to reedit these files if you want some other parameters running the python script. To see these type: 

```bash
python server.py --help for usages
```

- Then add game screens as you want them. To run them simply run game.sh for
linux users or game.bat for windows users. There is a need to reedit these files if you want some other parameters running the python script. 
To see these type:

```bash
python gamelogic/main.py --help for usages
```

- To actually play the game. The players can go into the link below and follow the instructions
    - http://localhost:8080/static/start.html

- Starting the game requires a GET signal to the same server on
    - http://localhost:8080/start

- To make the game screen connect to each other, also a POST start signal is needed on. TODO change it
    - http://localhost:8080/setup
