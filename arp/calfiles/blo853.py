import aipy as a

class AntennaArray(a.fit.AntennaArray):
    def sim_cache(self, *args, **kwds):
        return a.fit.AntennaArray.sim_cache(self, *args, **kwds)
    def sim(self, i, j, pol):
        ans = a.fit.AntennaArray.sim(self, i, j, pol)
        return ans

prms = {
    'loc': ('+37:55.1','-122:09.4'),
    'antpos': {
        0: [0., 0., 0.] ,
        1: [0., 37., 0.] ,
    }
}

def get_aa(freqs):
    location = prms['loc']
    antennas = []
    beam = a.fit.Beam(freqs)
    for i in range (len(prms['antpos'])):
        pos = prms['antpos'][i]
        antennas.append(a.fit.Antenna(pos[0], pos[1], pos[2], beam, amp=.05))
    aa = AntennaArray(prms['loc'], antennas)
    return aa

src_prms = {
    'Sun': {'jys':1e5},
}

def get_catalog(srcs=None, cutoff=None, catalogs=None):
    cat = a.src.get_catalog(srcs=srcs, cutoff=cutoff, catalogs=catalogs)
    cat.set_params(src_prms)
    return cat
