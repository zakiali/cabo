#! /usr/bin/env python
import aipy as a, numpy as n
import sys, optparse, os

o = optparse.OptionParser()
opts,args = o.parse_args(sys.argv[1:])

def mfunc(uv, p, d, f):
    crd,t,(i,j) = p
    nd = d/n.where(n.abs(d)==0,1,n.abs(d))
    return p,nd,f

for filename in args:
    print filename, '->', filename+'n'
    if os.path.exists(filename+'n'):
        print '     File exists... skipping.'
        continue
    uvi = a.miriad.UV(filename)
    uvo = a.miriad.UV(filename+'n', status='new')
    uvo.init_from_uv(uvi)
    uvo.pipe(uvi, mfunc=mfunc, raw=True,
        append2hist='NORM AMP: Normailize amplitudes in a uvfile.\n')
    del(uvo)

