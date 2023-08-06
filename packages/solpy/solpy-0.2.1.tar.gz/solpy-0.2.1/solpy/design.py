import copy
import geo
import epw

#sketchup may be a good way to input this data
input = """{"system_name":"HAPPY CUSTOMER",
        "address":"15013 Denver W Pkwy, Golden, CO",
        "zipcode":"80401",
        "phase":1,
        "voltage":240,
        "service":200,
        "homerun":150,
        "space":[(10,5)],
        "shading":[],
        "desired output":10000
            ]}"""

def fill(inverter, zipcode, acDcRatio = 1.2, mount="Roof", stationClass = 1, Vmax = 600, bipolar= True):
    """maximize array"""
    tDerate = {"Roof":30,
            "Ground":25,
            "Pole":20}
    name, usaf = geo.closestUSAF( geo.zipToCoordinates(zipcode), stationClass)
    maxV = inverter.array.panel.Vmax(epw.minimum(usaf))
    #NREL suggests that long term degradation is primarily current not voltage
    derate20 = .97
    minV = inverter.array.panel.Vmin(epw.twopercent(usaf),tDerate[mount]) * derate20
    #print "MinV", minV
    if inverter.vdcmax != 0:
         Vmax = inverter.vdcmax
    smax = int(Vmax/maxV)
    #range to search
    pTol = .30
    inverterNominal = inverter.Paco
    psize = inverter.array.panel.Pmax
    solutions = []

    Imax = max(inverter.idcmax,inverter.Pdco*1.0/inverter.mppt_low)
    stringMax = int(round(Imax/inverter.array.panel.Impp))+1

    #Diophantine equation
    for s in range(smax+1):
        if (s*minV) >= inverter.mppt_low:
            for p in range(stringMax):
                pRatio = p*s*psize*1.0/inverterNominal
                if pRatio < (acDcRatio*(1+pTol)) and \
                        pRatio > (acDcRatio*(1-pTol)):
                            inverter.array.shape = [s]*p
                            t = copy.deepcopy(inverter)
                            t.minV = s*minV
                            t.maxV = s*maxV
                            solutions.append(t)
    return solutions

def design(DCsize, panellist, inverterlist):
    """parts selection algorithm"""
    #create all valid inverter panel combinations for location
    validC = []
    for inverterModel in inverterlist:
        for panelModel in panellist:
            #expedite.
            system = inverters.inverter(inverterModel,\
                    modules.pvArray(modules.module(panelModel),[2]))
            validC += fill(system,zc)
    for i in validC:
        print i, i.array, i.array.output(1000)
    #Sort in size

    #create list plants of all permetations

    #constrain by space
    #I think space constraint is probably a tiling problem

    #model varaints
    #this probalby needs to be queue based

    #constrain by production limits

    #rank

    #return list of top 5 solutions

if __name__ == "__main__":
    import inverters
    import modules
    zc='27713'
    m = "Mage Solar : USA Powertec Plus 250-6 MNCS"
    inv = "Refusol: 20 kW 480V"
    ms = modules.module(m)
    system = inverters.inverter(inv,modules.pvArray(ms,[11]))
    s = fill(system,zc)
    for i in s:
        print i, i.ratio(),i.array.output(1000)
    inverterlist = ["SMA America: SB4000TL-US-22 (240V) 240V",
            "SMA America: SB6000US-11 240V",
            "Solectria: PVI 7500 (240V) 240V"
            ]
    panellist = [
            "Axitec : AC-250P-156-60S *","Mage Solar : USA Powertec Plus 300-6 PL" ]
    design(1E6,panellist, inverterlist)
