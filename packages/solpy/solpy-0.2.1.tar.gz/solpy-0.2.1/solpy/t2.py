import enphase
print help(enphase.system)
a = enphase.system(246792)
print a
print a.power_today().values

ind =  enphase.index()
print ind[0].power_today().values
