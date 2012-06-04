#! /usr/bin/env python
import aipy as a, numpy as n, pylab as plt
import sys, ephem, optparse

o = optparse.OptionParser()
o.set_description(__doc__)
a.scripting.add_standard_options(o, cal=True)
o.add_option('-p', dest='plot', action='store_true',
    help='plot the data in the two .npz files or not. specify the file names if option is given with the -f option. .') 
o.add_option('-f', '--files', dest='files', type='str', 
    help='files to plot in -p option is given.file name distinguished by a _.')
opts, args = o.parse_args(sys.argv[1:])

print opts.plot
if opts.plot:
    if opts.files == None:
        print 'specify filenames.'
        exit() 

deg2rad = n.pi/180.
rad2deg = 180/n.pi
if not opts.plot:

    sdf = .5/1024.

    freqs = n.arange(1024)*sdf + (sdf + .5) # IN GHz
    #set up observer.
    aa = a.cal.get_aa(opts.cal,freqs)
    sun = ephem.Sun()
    ad = {}
    ad['az'] = []
    ad['alt'] = []
    ad['ra'] = []
    ad['dec'] = []
    ad['times'] = []
    for file in args:
        print 'processing  %s'%file
        uvi = a.miriad.UV(file)
        #just need to pick one baseline b/c we want all times. 
        uvi.select('antennae',0,0)
        for p,d,f in uvi.all(raw=True): 
            crd, t, (i,j) = p 
            aa.set_jultime(t)
            sun.compute(aa)
            ad['times'].append(t)
            ad['az'].append(sun.az)
            ad['alt'].append(sun.alt)
            ad['ra'].append(sun.ra)
            ad['dec'].append(sun.dec)
    #       print sun.ra, sun.dec 

    for key in ad.keys():
        ad[key] = n.array(ad[key])

    print 'Saving data to ->',str(ad['times'][0])+'.npz'
    n.savez(str(ad['times'][0])+'.npz', **ad)

if opts.plot:
    f1,f2 = opts.files.split('_')
    d1 = n.load(f1) 
    d2 = n.load(f2) 
    plt.subplot(211)
    plt.title('az vs. alt')
    plt.xlabel('az')
    plt.ylabel('alt')
    plt.plot(d1['az']*rad2deg,d1['alt']*rad2deg,'.b',d2['az']*rad2deg,d2['alt']*rad2deg,'.r')
    plt.subplot(212)
    plt.title('ra vs. dec')
    plt.xlabel('ra')
    plt.ylabel('dec')
    plt.plot(d1['ra'],d1['dec'],'.b',d2['ra'],d2['dec'],'.r')
    plt.show()
