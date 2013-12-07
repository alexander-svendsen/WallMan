import requests
import time
import random

directions = ["left", "right", "up", "down"]

for i in xrange(0, 50):
    username = "username{0}".format(i)
    direction = directions[random.randint(0, 3)]
    data = '{"name": "' + username + '", "direction" : "' + direction + '"}'
    print data
    start = time.time()
    r = requests.post("http://rocksvv.cs.uit.no:35001/move", data=data)
    print r.text  # To read the request
    end = time.time()

    round_trip = end - start
    timestamp = time.strftime("%H:%M:%S", time.gmtime())
    with open('../measurement/master/delay.csv', 'a+') as csv_file:
        csv_file.write('{0}, {1}\n'.format(timestamp, round_trip))
