#! /usr/bin/env python
import aipy as a, numpy as n, os, sys

aa = a.phs.ArrayLocation(('+37:55.1','-122:09.4')) # Leuschner Observatory

#rewire = { 0:0, 1:-1, 2:-1, 3:1 }

for filename in sys.argv[1:]:
    print filename, '->', filename+'c'
    if os.path.exists(filename+'c'):
        print '    File exists... skipping.'
        continue
    uvi = a.miriad.UV(filename)
    uvo = a.miriad.UV(filename+'c', status='new')
    uvi.select('antennae',0,3) 
    c = 0
    for num in uvi.all():
        c+=1
    numint = c
    #t_base = float('.'.join(filename.split('.')[1:3])) - numint*(2**28/200e6)*(1/(60.*60*24))
    uvi.rewind()
    uvi.select('antennae',-1,-1)
    start_t = 0
    curtime = 0
    def mfunc(uv, p, d, f):
        global curtime, start_t
        crd,t,(i,j) = p
        #d,f = d[::-1],f[::-1]
        #_i,_j = rewire[i], rewire[j]
        #if _i == -1 or _j == -1: return p, None, None

        #if t != curtime:
        #    if start_t == 0: start_t = t
        #    _t = t_base + (t - start_t)
        #    aa.set_jultime(_t)
        #    uvo['lst'] = uvo['ra'] = uvo['obsra'] = aa.sidereal_time()
        #    curtime = t
        #_t = t_base + (t - start_t)
        f[:11] = 1
        f[49:61] = 1
        f[67] = 1
        f[73:85] = 1
        f[122:147] = 1
        f[160:221] = 1
        f[233:258] = 1 
        f[270:331] = 1
        f[342:356] = 1
        f[479:1024] = 1
        #f[:273] = 1
        #f[288:304] = 1
        #f[319:339] = 1
        #f[342:344] = 1
        #f[349:442] = 1
        #f[443] = 1
        #f[457:534] = 1
        #f[549:765] = 1
        #f[769] = 1
        #f[773] = 1
        #f[854:882] = 1
        #f[888:] = 1
        d = n.where(f, 0, d)
        return (crd,t,(i,j)),d,f

    override = {
        'lst': aa.sidereal_time(),
        'ra': aa.sidereal_time(),
        'obsra': aa.sidereal_time(),
        'sdf': 0.00048828125,
        'latitud': aa.lat,
        'dec': aa.lat,
        'obsdec': aa.lat,
        'longitu': aa.long,
        'sfreq': 0.5,
        'freq': 0.5,
        'inttime': 1.073741824,
        'nchan': 1024,
        'nants': 2,
        'ngains': 4,
        'nspect0': 2,
        'pol':a.miriad.str2pol['xx'],
        'telescop':'BAO',
        'antpos': n.transpose(n.array([
            [0., 0., 0.], #0
            [0., 0., 0.], #1 
            [0., 0., 0.], #2 
            [0., 0., 0.], #3 
        ])).flatten(),
    }

    uvo.init_from_uv(uvi, override=override)
    uvo.pipe(uvi, mfunc=mfunc, raw=True,
        append2hist=' '.join(sys.argv)+'\n')
    del(uvo)
