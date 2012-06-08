import aipy as a, numpy as n

class AntennaArray(a.fit.AntennaArray):
    def get_params(self, ant_prms={'*':'*'}):
        prms = a.fit.AntennaArray.get_params(self, ant_prms)
        for k in ant_prms:
            try: top_pos = n.dot(self._eq2zen, self[int(k)].pos)
            except(ValueError): continue
            if ant_prms[k] == '*':
                prms[k].update({'top_x':top_pos[0], 'top_y':top_pos[1], 'top_z':top_pos[2]})
            else:
                for val in ant_prms[k]:
                    if   val == 'top_x': prms[k]['top_x'] = top_pos[0]
                    elif val == 'top_y': prms[k]['top_y'] = top_pos[1]
                    elif val == 'top_z': prms[k]['top_z'] = top_pos[2]
        return prms
    def set_params(self, prms):
        for i, ant in enumerate(self):
            ant.pos = n.dot(n.linalg.inv(self._eq2zen), ant.pos)

prms = {
    'loc': ('+37:55.1','-122:09.4'),
    #equatorial nanoseconds.
    #Topocentric coordinates.
    #foot = 1ns
    #baselines : 2-3 = 26'2'' pureley e-w. (2-->3 is east direction)
             # :2-1 = 44'5''
             # :3-1 = 11'7.5'' ( 1 is south of 2 and 3 )
             # :2-0 = 41'9''
             # :3-0 = 27'2''
             # :1-0 = 23'8''
    #These are in topocentric nanosecond coordinates with antenna 0 as origin.
    'antpos': {
        0: [  0.0000,   0.0000, 0.000] ,
        1: [  5.0955,  23.5051, 0.000] , 
        2: [-32.8130,  26.8984, 0.000] , 
        3: [ -6.2206,  26.8984, 0.000] 
        },
    'delays': { 
        0: 0.0000, 
        1: 4.0000,
        2: 20.0000,
        3: 10.0000
        },
    'offsets':{}
}

def get_aa(freqs):
    location = prms['loc']
    antennas = []
    beam = a.fit.Beam(freqs)
    for i in range (len(prms['antpos'])):
        pos = prms['antpos'][i]
        dly = prms['delays'].get(i, 0.)
        off = prms['offsets'].get(i, 0.)
        antennas.append(a.fit.Antenna(pos[0], pos[1], pos[2], beam, phsoff = [dly,off],amp=.05,lat=prms['loc'][0]))
    aa = AntennaArray(prms['loc'], antennas)
    aa.set_params(prms)
    return aa

src_prms = {
    'Sun': {'jys':1e5},
}

def get_catalog(srcs=None, cutoff=None, catalogs=None):
    cat = a.src.get_catalog(srcs=srcs, cutoff=cutoff, catalogs=catalogs)
    cat.set_params(src_prms)
    return cat
 
