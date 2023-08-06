import pv
import json

p1 = """{"system_name":"HAPPY CUSTOMER",
        "address":"15013 Denver W Pkwy, Golden, CO",
        "zipcode":"80401",
        "phase":1,
        "voltage":240,
        "array":[
            {"inverter":"Enphase Energy: M215-60-2LL-S2x-IG-NA (240 V) 240V",
            "panel":"Mage Solar : Powertec Plus 250-6 PL",
            "quantity":20,
            "azimuth":180,
            "tilt":25
            }
            ]}"""
plant = pv.jsonToSystem(json.loads(p1))
b = plant.forecastOutput(source = 'blave')
print b.timeseries[0]
print b.values
print len(b.values)
print  sum(b.values)

f = plant.forecastOutput(source = 'forecast')
print f.timeseries[0]
print f.values
print len(f.values)
print  sum(f.values)

n = plant.forecastOutput(source = 'noaa')
print n.timeseries[0]

print n.values
print len(n.values)
print  sum(n.values)

