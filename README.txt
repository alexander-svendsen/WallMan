=======================================================================
*   __      __            ___    ___                                  *
*  /\ \  __/\ \          /\_ \  /\_ \    /'\_/`\                      *
*  \ \ \/\ \ \ \     __  \//\ \ \//\ \  /\      \     __      ___     *
*   \ \ \ \ \ \ \  /'__`\  \ \ \  \ \ \ \ \ \__\ \  /'__`\  /' _ `\   *
*    \ \ \_/ \_\ \/\ \_\.\_ \_\ \_ \_\ \_\ \ \_/\ \/\ \_\.\_/\ \/\ \  *
*     \ `\___ ___/\ \__/.\_\/\____\/\____\\ \_\\ \_\ \__/.\_\ \_\ \_\ *
*      '\/__//__/  \/__/\/_/\/____/\/____/ \/_/ \/_/\/__/\/_/\/_/\/_/ *
=======================================================================


## Requirements for running the game
- python 2.7.3 - http://www.python.org/
- pygame 1.9.3 - http://www.pygame.org/
- Flask 0.10 - http://flask.pocoo.org/
  and the tools flask need. Flask should install all of these by running: pip install Flask

If you want to run the test clients in the \testclient folder you will also need:
- Require 2.1.0 - http://requests.readthedocs.org/en/latest/


## How to use
1. start up the server
    - for linux:
        - run the server.sh file
    - for windows:
        - run the server.bat file

2. start up game instances (WARNING: you will need to configure the script first):
    - for linux:
        - run the game.sh file
    - for windows:
        -run the server.bat file


## Configuration. Need to be done inside the shell scripts to work
    - server:
        Change the python server.py [ARGUMENTS] with your arguments to configure it.

        usage: server.py [-h] [-ps PORT_SERVER] [-pm PORT_MASTER] [-sc SCREEN_CONFIG]
                         [-t TIME] [-m MEASURE]

        optional arguments:
          -h, --help            show this help message and exit
          -ps PORT_SERVER, --port_server PORT_SERVER
                                Server for http client port
          -pm PORT_MASTER, --port_master PORT_MASTER
                                Master port toward the game instances
          -sc SCREEN_CONFIG, --screen_config SCREEN_CONFIG
                                Pick a screen config of the available files inside the
                                screenconfig folder
          -t TIME, --time TIME
                                How long should the game run before it shutdown, in second
          -m MEASURE, --measure MEASURE
                                Should game resources be measured

    - game:
        Change the python game/main.py [ARGUMENTS] with your ARGUMENTS to configure it.

        usage: main.py [-h] [-a ADDRESS] [-p PORT] [-r RES RES] [-m MEASURE]

        Plays a game of Wallman. Note the external server must be active

        optional arguments:
          -h, --help            show this help message and exit
          -a ADDRESS, --address ADDRESS
                                Master address
          -p PORT, --port PORT
                                Master port
          -r RES RES, --res RES RES
                                Resolution of the screen
          -m MEASURE, --measure MEASURE
                                Should game resources be measured



## Playing a game session:
1. Start the server
2. Add game instances
3. Make the game instances connect to each other by sending: GET http://localhost:XXXX/setup
4. Go to: http://localhost:XXXX/static/start.html, to make a player join the game.
5. Start the game by sending: GET http://localhost:XXX/start
6. Play the game.


## What the different folders contain:
- game: The code for the game instances
    - graphics:         All the code to handle the graphical objects.
    - images:           All the images we are using in this project. Contains a README if some images is taken from somewhere.
    - maps:             All the map designs and a config file telling what the numbers represents.
    gameconnection.py   The communication class. Takes care of all communication from master and other game instances.
    main.py             The main game class. Runs the game and the logic. Contains the pygame code to update the view
    player.py           The player class. All the logic towards the player is moved here
    maptools.py         Handles reading in the maps from disk

- server: The code for the server
    - screenconfig:             Contains all the files aimed towards the screen configuration
    - static:                   Contains all the static files served by the master to the clients
    - masterconnectionpoint.py: Class to handle all communication to the game instances.
    - screenconfiguration.py:   Class to handle all the screen configuration buildup and reading
    - server.py:                Contains all the code aimed towards clients, builds the REST interface and such.

- socketcommunication: Socket communication classes, used by both the game and the server
- testclient: The code for the test clients, nothing to do with the rest of the folders
- tools: Measurement tools, used by both the game and the server for performence tests if turned on

