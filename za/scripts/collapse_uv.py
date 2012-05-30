#! /usr/bin/env python
import aipy as a, numpy, sys, os, optparse

o = optparse.OptionParser()
o.add_option('-n', '--nint', dest='nintegrations', type='int', default=10,
    help='The number of integrations to add up from a uvfile.')

opts,args = o.parse_args(sys.argv[1:])

aa = a.phs.ArrayLocation(('+37:55.1', '-122:09.4')) # Leuschner Obs.

nint2int = opts.nintegrations### this i the number of integrations to integrate together in the uv file.
UV_VAR_TYPES = {
    'source':   'a', 'operator': 'a', 'version':  'a', 'telescop': 'a',
    'antpos':   'd', 'freq':     'd', 'inttime':  'r', 'nants':    'i',
    'nchan':    'i', 'nspect':   'i', 'sfreq':    'd', 'sdf':      'd',
    'ischan':   'i', 'nschan':   'i', 'restfreq': 'd', 'npol':     'i',
    'epoch':    'r', 'veldop':   'r', 'vsource':  'r', 'longitu':  'd',
    'latitud':  'd', 'dec':      'd', 'obsdec':   'd', 'nspect':   'i',
    'ischan':   'i', 'epoch':    'r', 'veldop':   'r', 'vsource':  'r',
    'ra':       'd', 'obsra':    'd', 'lst':      'd', 'pol':      'i',
}

def inituv(uvi, uvo):
    '''initializes the uv variables for uvo file (needs to be created already) from the uvi file.'''
    for v in UV_VAR_TYPES:
        uvo.add_var(v, UV_VAR_TYPES[v])
    uvo['history'] = uvi['history'] 
    uvo['obstype'] = uvi['obstype']
    uvo['source'] = uvi['source']
    uvo['operator'] = uvi['operator']
    uvo['telescop'] = uvi['telescop']
    uvo['version'] = uvi['version']
    uvo['antpos'] =  uvi['antpos']
    uvo['nants'] = uvi['nants']
    uvo['npol'] =uvi['npol']
    uvo['epoch'] =uvi['epoch']
    uvo['nspect'] =uvi['nspect']
    uvo['ischan'] =uvi['ischan']
    uvo['veldop'] = uvo['vsource'] = uvi['veldop']
    uvo['longitu'] = uvi['longitu']
    uvo['latitud'] = uvo['dec'] = uvo['obsdec'] = uvi['latitud']
    uvo['sfreq'] = uvo['freq'] = uvo['restfreq'] = uvi['sfreq']
    uvo['sdf'] = uvi['sdf']
    uvo['nchan'] = uvo['nschan'] = uvi['nchan']
    uvo['bandpass']= uvi['bandpass']
    uvo['nspect0'] = uvi['nspect0']
    uvo['nchan0'] = uvi['nchan0']
    uvo['ntau'] = uvo['nsols'] = uvi['ntau']
    uvo['nfeeds'] = uvi['nfeeds']
    uvo['ngains'] = uvi['ngains']
    uvo['freqs'] = uvi['freqs']
    #this is what will change. Depending on how long of integration times we want.
    uvo['inttime'] = uvi['inttime']

for filename in sys.argv[1:]:
    print filename, '->', filename+'s'
    if os.path.exists(filename+'s'):
        print '        File exists.....skipping.'
        continue
    uvi = a.miriad.UV(filename)
    uvo = a.miriad.UV(filename+'s', status='new')
    inituv(uvi,uvo)
    c = 0
    #select one baseline to deduce the number of integrations in a file.
    uvi.select('antennae', 0, 1)
    for num in uvi.all():
        c +=1
    numint = c
    if c%nint2int !=0:
        print 'WARNING: Last %i integrations in input file will not be included in output file. '%(c%nint2int)
    uvi.rewind()
    #create dictionary to hold integrated data and number of integrations.
    sums = {}
    int = 0
    for i in range(4):
        for j in range(4)[i:]:
            sums[(i,j)] = [numpy.zeros(1024, dtype = numpy.complex64),int]
    uvi.select('antennae', -1, -1)
    #change integration time variable to reflect the new integration time.
    uvo['inttime'] = nint2int*uvi['inttime']
    for p, d, f in uvi.all(raw=True):
        #sums up the data 
        sums[p[2]][0] += d 
        #keeps track of the number of integrations.
        sums[p[2]][1] += 1
        # if the number of spectra integrated is nint2int, write it to the output file
        # and reinit the sums, not that the jd of the inegration is the last timestamp
        # of the summed spectra.
        if sums[p[2]][1] == nint2int:
            uvo['pol'] = a.miriad.str2pol['xx']
            uvo['ra'] = uvo['obsra'] = uvo['lst'] = aa.sidereal_time()
            uvo.write(p,sums[p[2]][0],f)
            sums[p[2]][0] = numpy.zeros(1024, dtype = numpy.complex64)
            sums[p[2]][1] = 0
    
    uvo._wrhd('history', uvo['history'] + 'collapsed along time axis. Int time = %f'%uvo['inttime'])
