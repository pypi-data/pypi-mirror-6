import pathfinder
import datetime
import pv
import json

blah = pathfinder.hourly(pathfinder.loadDict('/home/ncharles/pes/lehr.csv'))
print json.dumps(blah.month)
plant = pv.fileToSystem('/home/ncharles/pes/lehr.json')
print plant.hourlyShade.shade(datetime.datetime.now())
